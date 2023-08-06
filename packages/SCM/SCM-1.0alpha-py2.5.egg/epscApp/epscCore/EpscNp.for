C     Last change:  BC    7 Feb 102   12:26 pm
      PROGRAM EPSCNP
c **********************************************************************
c ***                  ***                   ***                     ***
c ***  PROGRAM EPSCNP  *** VERSION 27/jul/99 *** C.TOME, P.TURNER &  ***
c ***                  ***                   *** B. CLAUSEN          ***
c **********************************************************************
c ***  SUBROUTINES DIF_PLANES & EQUIV_PLANES MODIFIED TO INCLUDE
c ***  CUBIC CRYSTALS ON 14/02/95 AND AGAIN ON 20/04/95.
c ***  MINOR MODIFICATIONS IN MAIN ON 20/APR/95
c ***  MODIFIED TO CALCULATE RESIDUAL AND OVERALL STRAINS, AVERAGE
c ***  PLASTIC SHEARS IN DIFFRACTING SETS (JUNE 1997)
c ***  MODIFIED TO CALCULATE ESHELBY TENSOR USING GAUSS (07/08/97)
c ***  VOCE HARDENING INTRODUCED (13/02/98)
c **********************************************************************
c ***  MULTI-PHASE CODE, BUT ONLY ONE SITE.                          ***
c **********************************************************************
c ***                                                                ***
c *** SELF-CONSISTENT FORMULATION FOR THE POLYCRYSTALLINE AGGREGATE  ***
c *** OF ELASTO-PLASTIC SINGLE CRYSTALS WITH A SCHMID LAW.           ***
c *** IN THIS CODE IS IMPLEMENTED THE ELASTO-PLASTIC FORMULATION OF  ***
c *** HUTCHINSON,J.W., Proc.Roy.Soc.Lond. A 319,(1970) 247-272.      ***
c ***                                                                ***
c *** A fixed number of steps is imposed to reach the desired bounda ***
c *** ry conditions in stress-strain state.                          ***
c *** Selects the subset of active systems in each grain discarding  ***
c *** the system that has simple shear rate negative and the last    ***
c *** system in the stack of potentially active systems if the condi ***
c *** tion of active-loading is not fullfiled.                       ***
c ***                                                                ***
c **********************************************************************
c *** USES: av_modulus   :Calc. Voigt & Reuss averages               ***
c ***       cr_to_sa     :Transforms from Crystal to Sample system   ***
c ***       data_material:Reads material data                        ***
c ***       data_process :Reads process data                         ***
c ***       data_sample  :Reads sample data                          ***
c ***       dif_planes   :Calc. the residual strains in a direction  ***
c ***       equiv_planes :Sets the equivalent planes in a direction  ***
c ***       eshelby      :Calc. Eshelby tensor                       ***
c ***       euler        :Calc. transform matrix for each grain      ***
c ***       g_actsys     :Tests the potentially active systems       ***
c ***       g_average    :Does the average for the states            ***
c ***       g_modulus    :Calc. the el-pl moduli for each grain      ***
c ***       g_state      :Calc. the stress & strain rate in grain    ***
c ***       g_verify     :Checks the active loading condition        ***
c ***       invten       :Finds the inverse of 6x6 matrix            ***
c ***       esh_inv      :Contracted (Voigt) form of invten          ***
c ***       esh_mult     :Contracted (Voigt) multiplication          ***
c ***       lubksb       :Solves the set of N linear equations       ***
c ***       ludcmp       :Performs the LU decomposition of a matrix  ***
c ***       plasticity   :Evaluates plastic activity                 ***
c ***       sc           :Solves the iterative SC equation           ***
c ***       s_state      :Calc. the sample stress & strain rate      ***
c ***       svdcmp       :Does the Singular Value Decomposition      ***
c ***       temp_dep     :Calc. temp. dependent stiffness and CTE    ***
c ***       voigt        :Assigns the vectors and matrix in Voigt    ***
c ***       zirconium    :Calc. stiffness of temp. of Zr             ***
c ***                                                                ***
c **********************************************************************
c *** Includes the file with parameters and common statements        ***
c
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Variables types definitions:                                   ***
      CHARACTER*78 prosa
      CHARACTER*40 filemate(NPHX),filesamp(NPHX),fileproc(NPROCX)
      CHARACTER*40 fileprev,filediff(NPHX)
c ______________________________________________________________________
c
c *** Array dimensions:                                              ***
      DIMENSION ijvx(6,2),etsspl(6),etrsspl(6),e2(6,6)
      DIMENSION ng_up_int(0:10),wgt_up_int(0:10),tau_update_max(NGR)
      DIMENSION shear_tot_acum(NPHX),vfrac_tot_acum(NPHX)
c ______________________________________________________________________
c
c *** Initial data:                                                  ***
      DATA ((ijvx(i,j),j=1,2),i=1,6)/1,1,2,2,3,3,2,3,1,3,1,2/
c ______________________________________________________________________
c
c *** Read and write formats:                                        ***
    1 FORMAT(a)
    2 FORMAT(1h ,a)
    3 FORMAT(1h ,78('*'))
    4 FORMAT(1h ,'PURE ELASTIC SELFCONSISTENT PROBLEM')
    5 FORMAT(1h ,'START THE PROCESS: ',a)
    6 FORMAT(1h ,'STEP:',i4,'  CONTROL VARIABLE:',D13.5)
    7 FORMAT(1h ,6d12.4)
    8 FORMAT(1h ,'ITERATION OVER GRAINS MODULI - NUMBER: ',i3)
    9 FORMAT(1h ,'ABNORMAL PROGRAM STOP',/,1h ,'DOES NOT CONVERGE
     # AFTER ',i3,' ITERATIONS OVER GRAINS SYSTEMS')
   10 FORMAT(1h ,'PARTIAL TIME:',f8.2)
   11 FORMAT(1h ,'SELF-CONSISTENT MODULI:')
   12 FORMAT(1h ,'THERMAL COEFFCIENTS:')
   13 FORMAT(1h ,'STRESS-STRAIN STATE IN SAMPLE:')
   14 FORMAT(1h ,'STRESS-STRAIN STATE IN GRAINS:')
   15 FORMAT(1h ,'CRITICAL STRESS IN EACH GRAIN:')
   16 FORMAT(1h ,43f7.4)
   17 FORMAT(1h ,'TOTAL TIME:',f9.2)
   18 FORMAT(1h ,'NO SLIP ACTIVITY')
   19 FORMAT(1h ,'Percent respect to total shear:')
   20 FORMAT(1h ,'Mode #:',i3,2x,'Activity:',1x,f8.4,1x,'%')
   21 FORMAT(1h ,'NO TWIN ACTIVITY')
   22 FORMAT(1h ,'Twin mode:',i3,2x,'Volume fraction:',1x,f10.6)
   23 FORMAT(1h ,'               ','Percent:',1x,f8.4)
   24 FORMAT(1h ,12d12.4)
c
  100 FORMAT(1h ,14('*'),' SELF-CONSISTENT THERMO-ELASTOPLASTIC CODE'
     #,' "EPSC" ',14('*'))
  101 FORMAT(1h ,'PREVIOUS STRESS-STRAIN IN SAMPLE:')
  102 FORMAT(1h ,30('*'),' EPSC PROGRAM END ',30('*'))
c ______________________________________________________________________
c
c *** Assigns values to Voigt notation matrix (ijv), identity matrix ***
c *** (id2), product factor (profac) and inverse factor (invfac)     ***
      do i=1,6
         ijv(i,1)=ijvx(i,1)
         ijv(i,2)=ijvx(i,2)
         profac(i)=1.d0+(i/4)
         do j=1,6
            id2(i,j)=(i/j)*(j/i)*(1.d0-0.5d0*(i/4))
            invfac(i,j)=1.d0/((1+i/4)*(1+j/4))
         enddo
      enddo
c ______________________________________________________________________
c
c *** Initializes points and weights for Gaussian integration of Eshelby
c
      call eshelby3x3new(c4,c2,e2,axis,4,0)
c ______________________________________________________________________
c
c *** Opens the output files:
c ***                             SAMPLE:   "EPSC1.OUT" -> unit=11   ***
c *** Contains history and averages
c ***                             GRAINS:   "EPSC2.OUT" -> unit=12   ***
c *** Contains history over ngprn and statistics over grains.
c ***                             PLOT:     "EPSC3.OUT" -> unit=13   ***
c *** Components 11,22 & 33 of sample strain, stress, elastic strain
c *** and average number of active systems.
c ***                             ENDSTATE: "EPSC4.OUT" -> unit=14   ***
c *** Contains state in sample and grains after process. Used as starting
c *** file in following runs.
c ***                             TOTALET:  "EPSC5.OUT" -> unit=15   ***
c *** Contains average strain components and deviations. Also strain rates.
c ***                             TOTALST:  "EPSC6.OUT" -> unit=16   ***
c *** Contains average stress components and deviations. Also stress rates.
c ***                             %ACTIV:   "EPSC7.OUT" -> unit=17   ***
c *** Contains evolution of relative activity of plastic systems.
c ***                             EQUIV:    "EPSC8.OUT" -> unit=18   ***
c *** Contains evolution of overall equivalent magnitudes: stress, strain,
c *** plastic strain, (same for rates), accumulated total and plastic energy.
c ***                             RESIDUAL: "EPSC9.OUT" -> unit=19   ***
c *** Contains internal strain for each step in the diffraction planes and
c *** the diffracting direction.
c ***                             PLASTIC: "EPSC10.OUT" -> unit=20   ***
c *** Contains plastic activity in diffracting sets of grains.
c
      OPEN(unit=11,file='epsc1.out',status='unknown')
      OPEN(unit=12,file='epsc2.out',status='unknown')
      OPEN(unit=13,file='epsc3.out',status='unknown')
      OPEN(unit=14,file='epsc4.out',status='unknown')
      OPEN(unit=15,file='epsc5.out',status='unknown')
      OPEN(unit=16,file='epsc6.out',status='unknown')
      OPEN(unit=17,file='epsc7.out',status='unknown')
      OPEN(unit=18,file='epsc8.out',status='unknown')
      OPEN(unit=19,file='epsc9.out',status='unknown')
      OPEN(unit=20,file='epsc10.out',status='unknown')
      OPEN(unit=21,file='epsc11.out',status='unknown')
c
c *** Opens main control file: "EPSCNP.IN"   -> unit=1                 ***
      OPEN(unit=1,file='epscnp.in',status='old')
c *** Reads from "EPSCNP.IN":                                          ***
c *** Title of the simulation                                        ***
      read(1,1) prosa
      write(*,3)
      write(*,100)
      write(*,2) prosa
      write(*,3)
c *** Writes the title in the output files                           ***
      do iunit=11,19
         write(iunit,3)
         write(iunit,2) prosa
         write(iunit,3)
      enddo
c *** Number of PHASES                                               ***
      read(1,1) prosa
      read(1,*) nph
      if (nph.gt.NPHX) then
         write(*,'(1h ,''ERROR: Number of phases greater''
     #        ,'' than code dimension !!!'',/,1h 
     #        ,''DIMENSION in code = '',i3)') NPHX
         write(*,*)
         write(*,'(1h ,''STOP IN MAIN *** epsc ***'')')
         read(*,*)
         stop
      endif
c *** Volume fractions of phases                                     ***
      do iph=1,nph
         read(1,1) prosa
         read(1,*) wph(iph)
      enddo
      temp = 0.d0
      do iph=1,nph
         temp = temp + wph(iph)
      enddo
      if(dabs(temp-1.d0).gt.1.0e-3) then
         write(*,'(1h ,''ERROR: Volume fractions of phases''
     #        ,'' should add up to 1 !!!'')')
         write(*,*)
         write(*,'(1h ,''STOP IN MAIN *** epsc ***'')')
C         read(*,*)
         stop
      endif
c *** Name of MATERIAL file                                          ***
      do iph=1,nph
         read(1,1) prosa
         read(1,1) filemate(iph)
      enddo
c *** Name of SAMPLE file                                            ***
      do iph=1,nph
         read(1,1) prosa
         read(1,1) filesamp(iph)
      enddo
c *** Flag for previous procedure and the file name                  ***
      read(1,1) prosa
      read(1,*) i_prev_proc
      read(1,1) fileprev
c *** Flag for difraction directions and the file name               ***
      do iph=1,nph
         read(1,1) prosa
         read(1,*) i_diff_dir(iph)
         read(1,1) filediff(iph)
      enddo
c *** Number of thermomechanical process in this simulation          ***
      read(1,1) prosa
      read(1,*) nproc
      if (nproc.gt.NPROCX) then
         write(*,'(1h ,''ERROR: Number of processes greater''
     #        ,'' than code dimension !!!'',/,1h 
     #        ,''DIMENSION in code = '',i3)') NPROCX
         write(*,*)
         write(*,'(1h ,''STOP IN MAIN *** epsc ***'')')
         read(*,*)
         stop
      endif
c *** Names PROCESS files                                            ***
      read(1,1) prosa
      do n=1,nproc
         read(1,1) fileproc(n)
      enddo
      CLOSE(unit=1)
c ______________________________________________________________________
c
c *** Writes the identification of each output file                  ***
      write(11,2) 'FILE FOR SAMPLE AND CONVERGENCE'
      write(12,2) 'FILE FOR GRAINS STATE AND PLASTIC ACTIVITY'
      write(13,2) 'COMPONENTS 11 22 33 OF SAMPLE STRAIN, STRESS,
     # ELASTIC STRAIN, AVACS, PHASE STRAINS, PHASE STRESSES AND 
     # ELASTIC PHASE STRAINS'
      write(14,2) 'FINAL SAMPLE AND GRAINS STATE'
      write(15,2) 'EVOLUTION OF SAMPLE STRAIN RATE, STRAIN (and devs)'
      write(15,2) 'ETRSS - ETRDEV - ETSS - ETDEV (6 components each):'
      write(16,2) 'EVOLUTION OF SAMPLE STRESS RATE, STRESS (and devs)'
      write(16,2) 'STRSS - STRDEV - STSS - STDEV (6 components each):'
      write(17,2) 'RELATIVE ACTIVITY IN EACH MODE AND AVACS vs STRAIN'
      write(17,2) 'SLIP AND TWINNING MODES ACTIVITY STATISTIC:'
      write(18,2) 'EQUIVALENT STATES'
      write(18,2) 'EQ ET - EQ PL ET - EQ ST - EQ ETR - EQ PL ETR'
     #     ,' - EQ STR - VOLUME - PRESSURE - WTOT - WPLTOT'
     #     ,' - STET - STETAV'
      write(19,2) 'EVOLUTION OF INTERNAL STRAINS'
      do iunit=11,19
         write(iunit,3)
      enddo
      do i=1,6
        write(13,"($2x,a,I1.1,a)") 'EPS',i,'      '
      enddo
      do i=1,6
        write(13,"($2x,a,I1.1,a)") 'SIG',i,'      '
      enddo
      do i=1,6
        write(13,"($2x,a,I1.1,a)") 'EEPS',i,'     '
      enddo
      write(13,"($2x,a)") '   ACTAV  '
      do iph=1,nph
        do i=1,6
          write(13,"($2x,a,I1.1,a,I1.1,a)") 'ph',iph,'_EPS',i,'  '
        enddo
      enddo
      do iph=1,nph
        do i=1,6
          write(13,"($2x,a,I1.1,a,I1.1,a)") 'ph',iph,'_SIG',i,'  '
        enddo
      enddo
      do iph=1,nph
        do i=1,6
          write(13,"($2x,a,I1.1,a,I1.1,a)") 'ph',iph,'_EEPS',i,' '
        enddo
      enddo
      write(13,*)
c ______________________________________________________________________
c
c *** Calls the routines for the input data:"data_material"-> MATERIAL***
c ***                                       "data_sample"  -> SAMPLE  ***
      call data_material(filemate)
      call data_sample  (filesamp,i_prev_proc,fileprev)
c
c *** If there is twinning reorientation initializes specific arrays
      do iph=1,nph
         ioption=0
         call twinning(ioption,iph)
      enddo
c ______________________________________________________________________
c
c *** Calls the routine to rotate from crystal to sample.             ***
c *** Option 0: rotate Schmid tensors & thermal coefficients          ***
c ***        1: rotate elastic stiffnes                              ***
      ng1=1
      ng2=ngrain
      call cr_to_sa(ng1,ng2,0)
      call cr_to_sa(ng1,ng2,1)
c     ______________________________________________________________________
c
c *** Calls DIF_PLANES to define the sets of grains that have one    ***
c *** crystallographic plane along each diffraction direction.       ***
c *** The OPTION=1 call calculates initial strain in those planes    ***
      call dif_planes(filediff,0.d0,0,0)
      call dif_planes(filediff,0.d0,0,1)
c ______________________________________________________________________
c
c *** If there is no previous procedure:                             ***
      if (i_prev_proc.eq.0) then
c *** Calc. average elastic stiffness and compliance (Voigt, Reuss, Hill)
         call av_modulus
c *** Solves the pure elastic problem.                               ***
         write(*,4)
         write(11,4)
         do ng=1,ngrain
            gamtot(ng)=0.d0
            do i=1,6
               do j=1,6
                  acs2(i,j,ng)=ccs2(i,j,ng)
               enddo
            enddo
         enddo
         liter=0
         itmax_mod=100
         error_mod=1.d-03
         write(*,*)
         call sc(0,liter,iverify,e2)
         call invten (ass2,sss2)
         write(11,*)
         write(11,*) 'SELF CONSISTENT ELASTIC STIFFNESS'
         write(11,'(6D12.4)') ass2
         write(11,*)
         write(11,*)
         write(11,*) 'SELF CONSISTENT ELASTIC COMPLIANCE'
         write(11,'(6D12.4)') sss2
         write(11,*)
         write(11,3)
c     
      else
c
c *** Calc. the interaction tensor to be used in sample states calc. ***
         call sc(1,liter,iverify,e2)
      endif
c ______________________________________________________________________
c
c *** Sets the variable for the BREAK control                        ***
c      breakrcvd=.false.
c      call break(breakrcvd)
c ______________________________________________________________________
c
      do iph=1,nph
         if(ndiff(iph).gt.0) then
            do nd=1,ndiff(iph)
               shear_dif_acum(nd,iph)=0.d0
            enddo
         endif
      enddo
c
c *** Opens the loop for the different processes                     ***
c *** Sets the step as a fixed unit step                             ***
      step=1.d0
      time_acum=0.d0
      np=0
c      do while(np.lt.nproc.and..not.(breakrcvd))
      do while(np.lt.nproc)
         np=np+1
c         call timer(itime_start)
        call cpu_time(start_time)
         do iph=1,nph
            do mo=1,nmodes(iph)
               shear_mod_acum(mo,iph)=0.d0
               vfrac_mod_acum(mo,iph)=0.d0
            enddo
         enddo
         wtotal=0.d0
         wplastic=0.d0
         nout_old=0
         do iph=1,nph
            do ng=1+ngrph(iph-1),ngrph(iph)
               ng_update(ng)=0
               do ns1=1,nsys(iph)
                  tau_update(ns1,ng)=1.d0
               enddo
            enddo
         enddo
c ______________________________________________________________________
c
c *** Calls the routine for the input data: "data_process" -> PROCESS***
         call data_process(fileproc(np),i_temp_cij,i_et_0,i_control_var)
c ______________________________________________________________________
c
c *** If i_et_0=1 resets total strain in sample and crystals to zero.
c *** This is done for redefining the origin when plotting, but does not
c     alter the stress states or the elastic strains.
c *** Total strains are updated incrementally at each step using the
c     strain rates calculated in the step.
c *** A modification by CNT on 15/07/98 permits to refer 'elastic' strain
c     in grains to the values of the previous process (for comparing with
c     X-ray or neutron measurements).
c
         if (i_et_0.eq.1) then
            do i=1,6
               etss(i)=0.d0
            enddo
            do ng=1,ngrain
               do i=1,6
                  etcs(i,ng)=0.d0
                  stcsref(i,ng)=stcs(i,ng)
               enddo
            enddo
         endif
c
         if (np.eq.1) then
            write(13,'(3(6e12.4),f12.5,6(6e12.4))')
     #           (etss(i),i=1,6),
     #           (stss(j),j=1,6),
     #           (etelss(k),k=1,6),actav,
     #           ((etssph(i,iph),i=1,6),iph=1,nph),
     #           ((stssph(i,iph),i=1,6),iph=1,nph),
     #           ((etelssph(i,iph),i=1,6),iph=1,nph)
c            write(13,'(3(3d12.4,3x),f10.4,6(3x,3d12.4))')
c     #           (etss(i),i=1,3),(stss(j),j=1,3),(etelss(k),k=1,3),
c     #           actav,((stssph(i,iph),i=1,3),iph=1,2),
c     #           ((etssph(i,iph),i=1,3),iph=1,2),
c     #           ((etelssph(i,iph),i=1,3),iph=1,2)
c            write(13,'(3(3d12.4,3x),f10.4)') (etss(i),i=1,3),
c     #           (stss(j)*1e3,j=1,3),(etelss(k),k=1,3),actav
         end if
c ______________________________________________________________________
c
c *** Calculates the stress or strain rate boundary condition with respect
c *** to a unit time interval.
         do i=1,6
            strbc(i)=0.d0
            if (istbc(i).eq.1) strbc(i)=(stbc(i)-stss(i))/nsteps
            etrbc(i)=0.d0
            if (ietbc(i).eq.1) etrbc(i)=(etbc(i)-etss(i))/nsteps
         enddo
c *** If the starting temperature is different from the final temperature
c *** evaluates the temp. increment in each step
         deltemp=0.d0
         if (dabs(temp_s-temp_f) .gt. 1.e-3) then
            deltemp=(temp_f-temp_s)/nsteps
         endif
         temp=temp_s
c ______________________________________________________________________
c
c *** Does the loop for the steps until the boundary conditions      ***
         write(*,3)
         write(*,3)
         write(*,5) fileproc(np)
         do iunit=11,12
            write(iunit,3)
            write(iunit,3)
            write(iunit,5) fileproc(np)
         enddo
         ns=0
c        do while (ns.lt.nsteps.and..not.(breakrcvd))
         do while (ns.lt.nsteps)
c
            if (i_control_var.eq.0) xref=temp
            if (i_control_var.ge.1) xref=etss(i_control_var)
            if (i_control_var.ge.4) xref=stss(i_control_var-3)
c
            ns=ns+1
            write(*,6) ns,xref
            write(*,101)
            write(*,7) stss
            write(*,7) etss
            write(*,*)
            write(11,6) ns,xref
            write(12,6) ns,xref
c
c *** Resets to zero the shear increments before starting new deformation step.
            do iph=1,nph
               do ng=1+ngrph(iph-1),ngrph(iph)
                  do isys=1,nsys(iph)
                     gamd(isys,ng)=0.d0
                  enddo
               enddo
            enddo
c
c *** If deltemp is not equal zero then call subroutine that         ***
c *** evaluates the single crystal stiffness and CTE's               ***
c *** The user have to supply the description of the temperature     ***
c *** dependence. Examples are given for Zirconium ans Zinc          ***
c *** For multi phase calculations you must also pass the phase      ***
c *** number to the subroutine                                       ***
            if (i_temp_cij.eq.1.and.deltemp.ne.0.d0) then
c               call zirconium(temp)
               call zinc(temp,1)
               call zinc(temp,2)
               ng1=1
               ng2=ngrain
               call cr_to_sa(ng1,ng2,1)
            endif
c
c *** Does a loop to find the sets of active systems in all grains   ***
c *** that satisfy the overall problem                               ***
            it_grain=0
            iverify=1
            do while (iverify.ne.0.and.it_grain.lt.itmax_grain)
               it_grain=it_grain+1
               write(11,8) it_grain
c
c *** Checks for the potentially active systems in each grain        ***
               call g_actsys(nout_old)
c     
c *** Solves the equation system to find the sample stress rate and  ***
c *** strain rate                                                    ***
               call s_state
c
c *** Searchs for the set of active loading systems in each grain    ***
               call g_modulus
c
c *** Solves for the self-consistent polycrystal modulus             ***
               call sc(2,it_grain,iverify,e2)
c
c *** Closes the verify (iverify) loop                               ***
               write(11,*)
            enddo
c
c *** If after itmax_grain iterations does not reach convergence the ***
c *** program stops                                                  ***
            if (it_grain.eq.itmax_grain) then
               write(11,*)
               write(11,9)
               write(*,*)
               write(*,9)
               read(*,*)
               stop
            endif
c
c *** Calc. the polycrystal's and grains' states                     ***
c         call s_state
c         do ng=1,ngrain
c           call g_state(ng)
c         enddo
c
c *** Calls the routine to calculate plastic activity                ***
            call plasticity(step,temp,i_control_var)
c *** Calls the routine to calculate twinning transf. & reorientation
            do iph=1,nph
               if (ntwsys(iph).gt.0) then
                  ioption=1
                  call twinning(ioption,iph)
               end if
            enddo
c
c *** A calculation of plastic strain in diffracting families (for Tom Holden)
c         nskip=ns/10*10
c         if(ndiff.gt.0) then
c           if(nskip.eq.ns .or. ns.eq.nsteps) then
c             ixx=i_control_var
c             write(20,'(i5,f10.4,(5x,20f9.5))') ns,etss(ixx),
c    #                           (shear_dif_acum(nd),nd=1,ndiff)
c
c *** Temporary output of Eshelby tensor for comparison and benchmarking
c             write(20,'('' eshelby tensor at step'',i5)') ns
c             write(20,'(6f12.6)') ((e2(i,j),j=1,6),i=1,6)
c           endif
c         endif
c
c *** Updates the state in each grain and in sample                  ***
            do iph=1,nph
               do ng=1+ngrph(iph-1),ngrph(iph)
                  if(nact(ng).ne.0) then
                     do ns1=1,nsys(iph)
                        tau(ns1,ng)=tau(ns1,ng)+taud(ns1,ng)*step
                        gamtot(ng)=gamtot(ng)+gamd(ns1,ng)*step
                     enddo
                  endif
               enddo
            enddo
            do i=1,6
               stss(i)=stss(i)+strss(i)*step
               etss(i)=etss(i)+etrss(i)*step
               do ng=1,ngrain
                  stcs(i,ng)=stcs(i,ng)+strcs(i,ng)*step
                  etcs(i,ng)=etcs(i,ng)+etrcs(i,ng)*step
               enddo
            enddo
            temp=temp+deltemp
c
c *** Calls the routine to calculate averages and deviations         ***
c
            nskip=ns/1*1
            if (ns.eq.1 .or. ns.eq.nsteps .or. ns.eq.nskip) then
               call g_average
            endif
c
c *** Calculates macroscopic elastic strain                          ***
c *** Writes total strain, stress, avacs and elastic strain          ***
c
            do i=1,6
               etelss(i)=0.d0
               do j=1,6
                  etelss(i)=etelss(i)+sss2(i,j)*stss(j)*profac(j)
               enddo
            enddo
c
            write(13,'(3(6e12.4),f12.5,6(6e12.4))')
     #           (etss(i),i=1,6),
     #           (stss(j),j=1,6),
     #           (etelss(k),k=1,6),actav,
     #           ((etssph(i,iph),i=1,6),iph=1,nph),
     #           ((stssph(i,iph),i=1,6),iph=1,nph),
     #           ((etelssph(i,iph),i=1,6),iph=1,nph)
c            write(13,'(3(3d12.4,3x),f10.4,6(3x,3d12.4))')
c     #           (etss(i),i=1,3),(stss(j),j=1,3),(etelss(k),k=1,3),
c     #           actav,((stssph(i,iph),i=1,3),iph=1,2),
c     #           ((etssph(i,iph),i=1,3),iph=1,2),
c     #           ((etelssph(i,iph),i=1,3),iph=1,2)
c            write(13,'(3(3d12.4,3x),f10.4,2(3x,3d12.4))') 
c     #           (etss(i),i=1,3),(stss(j)*1e3,j=1,3),(etelss(k),k=1,3),
c     #           actav,((etelssph(i,iph),i=1,3),iph=1,2)
c
c *** Do if there are sets of grains to average for diffaction.      ***
c
c       nskip=ns/nsteps*nsteps
c       if (ns.eq.1 .or. ns.eq.nsteps .or. ns.eq.nskip) then
c            if (ns.eq.nsteps) then
               call dif_planes(filediff,temp,i_control_var,3)
               call dif_planes(filediff,temp,i_control_var,1)
c            endif
c       endif
c
c *** Calc. the equivalent states and energies                       ***
            stsseq=0.d0
            strsseq=0.d0
            etsseq=0.d0
            etrsseq=0.d0
            etsspleq=0.d0
            etrsspleq=0.d0
            do i=1,6
               etsspl(i)=etss(i)
               etrsspl(i)=etrss(i)
               do j=1,6
                  etsspl(i)=etsspl(i)-sss2(i,j)*stss(j)*profac(j)
                  etrsspl(i)=etrsspl(i)-sss2(i,j)*strss(j)*profac(j)
               enddo
               stsseq=stsseq+stss(i)*stss(i)*profac(i)
               strsseq=strsseq+strss(i)*strss(i)*profac(i)
               etsseq=etsseq+etss(i)*etss(i)*profac(i)
               etrsseq=etrsseq+etrss(i)*etrss(i)*profac(i)
               etsspleq=etsspleq+etsspl(i)*etsspl(i)*profac(i)
               etrsspleq=etrsspleq+etrsspl(i)*etrsspl(i)*profac(i)
            enddo
            stsseq=dsqrt(3.d0/2.d0*stsseq)
            strsseq=dsqrt(3.d0/2.d0*strsseq)
            etsseq=dsqrt(2.d0/3.d0*etsseq)
            etrsseq=dsqrt(2.d0/3.d0*etrsseq)
            etsspleq=dsqrt(2.d0/3.d0*etsspleq)
            etrsspleq=dsqrt(2.d0/3.d0*etrsspleq)
            pressure=-(1.d0/3.d0)*(stss(1)+stss(2)+stss(3))
            volume=(etss(1)+etss(2)+etss(3))
            stet=0.d0
            do i=1,6
               wtotal=wtotal+stss(i)*etrss(i)*profac(i)*step
               wplastic=wplastic+stss(i)*etrsspl(i)*profac(i)*step
               stet=stet+stss(i)*etss(i)*profac(i)
            enddo
            stetav=0.d0
            do ng=1,ngrain
               do i=1,6
                  stetav=stetav+stcs(i,ng)*etcs(i,ng)*profac(i)*wgt(ng)
               enddo
            enddo
            write(18,24) etsseq,etsspleq,stsseq,etrsseq,etrsspleq
     #           ,strsseq,volume,pressure,wtotal,wplastic,stet,stetav
c
c *** Closes the steps (ns) loop                                     ***
            write(*,3)
            write(11,3)
            write(12,3)
         enddo
c
c *** makes statistic and histogram on stress along diffraction directions
c        if (i_diff_dir(iph) .eq. 1) then
c          call dif_planes (filediff,temp,i_control_var,2)
c        endif
c         call timer(itime_end)
c         time=(itime_end-itime_start)/100.d0
        call cpu_time (end_time)
        time=end_time-start_time
         time_acum=time_acum+time
         write(11,*)
         write(11,3)
         write(11,10) time
         write(11,3)
         write(*,*)
         write(*,3)
         write(*,10) time
         write(*,3)
         write(12,*)
         do iph=1,nph
            shear_tot_acum(iph)=0.d0
            vfrac_tot_acum(iph)=0.d0
            do mo=1,nmodes(iph)
               shear_tot_acum(iph)=shear_tot_acum(iph) 
     #              + shear_mod_acum(mo,iph)
               vfrac_tot_acum(iph)=vfrac_tot_acum(iph)
     #              + vfrac_mod_acum(mo,iph)
            enddo
         enddo
         do iph=1,nph
            if (shear_tot_acum(iph).eq.0.d0) then
               write(12,18)
            else
               write(12,19)
               do mo=1,nmodes(iph)
                  write(12,20) mo,shear_mod_acum(mo,iph)/
     #                 shear_tot_acum(iph)*100.d0
               enddo
            endif
            if (vfrac_tot_acum(iph).eq.0.d0) then
               write(12,21)
            else
               do mo=1,nmodes(iph)
                  if (itw(mo,iph).eq.1) then
                     write(12,22) mo,vfrac_mod_acum(mo,iph)
                     write(12,23) vfrac_mod_acum(mo,iph)/
     #                    vfrac_tot_acum(iph)*100.d0
                  endif
               enddo
            endif
         enddo
c        write(12,*)
c        write(12,3)
c        write(12,*)
c        write(12,*) 'UPDATE OF SCYS DUE TO OUT CONDITION:'
         tau_up_max=0.d0
         ng_up_tot=0
         wgt_up_tot=0.d0
         do iph=1,nph
            do ng=1+ngrph(iph-1),ngrph(iph)
               tau_update_max(ng)=0.d0
c          write(12,16) (tau_update(n,ng),n=1,nsys)
               ng_up_tot=ng_up_tot+ng_update(ng)
               wgt_up_tot=wgt_up_tot+wgt(ng)*ng_update(ng)
               do n=1,nsys(iph)
                  if (tau_update(n,ng).gt.tau_up_max) then
                     tau_up_max=tau_update(n,ng)
                  endif
                  if (tau_update(n,ng).gt.tau_update_max(ng)) then
                     tau_update_max(ng)=tau_update(n,ng)
                  endif
               enddo
            enddo
         enddo
         ntau_up_write=0
         ng_up_int(0)=ngrain
         wgt_up_int(0)=1.d0
         if (tau_up_max.gt.1.d0) then
            ntau_up_write=1
            tau_up_int=(tau_up_max-1.D0)/10.d0
            do nint=1,10
               ng_up_int(nint)=0
               wgt_up_int(nint)=0.d0
               do ng=1,ngrain
                  if(tau_update_max(ng).gt.1.d0+(nint-1)*tau_up_int.and.
     #                 tau_update_max(ng).le.1.d0+nint*tau_up_int) then
                     ng_up_int(nint)=ng_up_int(nint)+1
                     wgt_up_int(nint)=wgt_up_int(nint)+wgt(ng)
                  endif
               enddo
               ng_up_int(0)=ng_up_int(0)-ng_up_int(nint)
               wgt_up_int(0)=wgt_up_int(0)-wgt_up_int(nint)
            enddo
         endif
         write(12,*)
         write(12,*) 'TAU_UPDATE_MAX = ',tau_up_max
         write(12,*) 'TOTAL NUMBER OF GRAINS UPDATED = ',ng_up_tot
         write(12,*) 'VOLUME FRACTION UPDATED = ',wgt_up_tot
         write(12,*) '% OF VOLUME FRACTION UPDATED = ',wgt_up_tot*100.d0
         write(12,*) 'STATISTIC FOR NON-HARDENING UPDATE OF SCYS:'
         write(12,*) '(DONE OVER MAXIMUM VALUE IN EACH GRAIN)'
         write(12,'(1h ,i5,'' grains that represent '',f6.2,
     #        ''% volume fraction were not updated'')') ng_up_int(0)
     #        ,wgt_up_int(0)*100.d0
         if (ntau_up_write.eq.1) then
            write(12,'(1h ,
     #           ''# GRAINS    WGT   %WGT   INITIAL   FINAL'')')
            do nint=1,10
               write(12,'(1h ,1x,i5,4x,f6.4,1x,f6.2,3x,f6.4,1x,f6.4))')
     #              ng_up_int(nint),wgt_up_int(nint),wgt_up_int(nint)
     #              *100.d0,1.d0+(nint-1)*tau_up_int
     #              ,1.d0+nint*tau_up_int
            enddo
         endif
         write(12,*)
         write(12,3)
c ______________________________________________________________________
c
c *** Closes the process (np) loop                                   ***
      enddo
c ______________________________________________________________________
c
c *** Writes in "EPSC4.OUT" (unit=14) the final state                ***
      write(14,11)
      write(14,7) ass2
      write(14,12)
      write(14,7) alfass
      write(14,13)
      write(14,7) stss
      write(14,7) etss
      write(14,7) etelss
      write(14,14)
      do ng=1,ngrain
         write(14,7) (stcs(i,ng),i=1,6)
c        write(14,'(f12.5)') (stcs(1,ng)+stcs(2,ng)+stcs(3,ng))/3.
         write(14,7) (etcs(i,ng),i=1,6)
      enddo
      write(14,15)
      do iph=1,nph
         do ng=1+ngrph(iph-1),ngrph(iph)
            write(14,16) ((tau(n,ng)/tau0(n,iph)),n=1,nsys(iph)),
     #           gamtot(ng)
         enddo
      enddo
c ______________________________________________________________________
c
c *** Closes the output files:        "EPSCx.OUT" -> unit=1x         ***
      write(11,*)
      write(11,3)
      write(11,17) time_acum
      write(11,3)
      do iunit=11,21
         CLOSE(unit=iunit)
      enddo
      write(*,*)
      write(*,3)
      write(*,17) time_acum
      write(*,3)
      write(*,102)
      write(*,3)
c ______________________________________________________________________
c
c *** End the "EPSC program"                                         ***
C      read(*,*)
C      stop
      END
c
c **********************************************************************
c **** SUBROUTINES OF EPSC *** ORIGINAL VERSION 12/OCT/94 ***  P. TURNER
c **** LAST MODIFIED ON 23/AUG/98
c **********************************************************************
c
      SUBROUTINE av_modulus
c **********************************************************************
c *** Calc. the VOIGT, REUSS and HILL averages for the elastic mod.  ***
c **********************************************************************
c *** USES:    invten                                                ***
c **********************************************************************
c *** VERSION: 12/OCT/94                                             ***
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Array dimensions:                                              ***
      DIMENSION css2vo(6,6),css2re(6,6)
      DIMENSION sss2vo(6,6),sss2re(6,6)
c ______________________________________________________________________
c
c *** Read and write formats:                                        ***
    1 FORMAT(1h ,'ELASTIC PROPERTIES AVERAGE:')
    2 FORMAT(1h ,6d12.4)
    3 FORMAT(1h ,78('*'))
c ______________________________________________________________________
c
c *** Starts the calculations                                        ***
      do i=1,6
        do j=1,6
          css2vo(i,j)=0.d0
          sss2re(i,j)=0.d0
        enddo
      enddo
c
      do ng=1,ngrain
        do i=1,6
          do j=1,6
            css2vo(i,j)=css2vo(i,j)+wgt(ng)*ccs2(i,j,ng)
            sss2re(i,j)=sss2re(i,j)+wgt(ng)*scs2(i,j,ng)
          enddo
        enddo
      enddo
      write(11,1)
      write(11,*)
      write(11,*) ' VOIGT average stiffness matrix'
      write(11,2) ((css2vo(i,j),j=1,6),i=1,6)
      call invten(css2vo,sss2vo)
      write(11,*)
      write(11,*) ' VOIGT average compliance matrix'
      write(11,2) ((sss2vo(i,j),j=1,6),i=1,6)
      write(11,*)
      write(11,*)
      write(11,*) ' REUSS average compliance matrix'
      write(11,2) ((sss2re(i,j),j=1,6),i=1,6)
      call invten(sss2re,css2re)
      write(11,*)
      write(11,*) ' REUSS average stiffness matrix'
      write(11,2) ((css2re(i,j),j=1,6),i=1,6)
c
      do i=1,6
        do j=1,6
          css2(i,j)=(css2vo(i,j)+css2re(i,j))/2.d0
          ass2(i,j)=css2(i,j)
        enddo
      enddo
      write(11,*)
      write(11,*)
      write(11,*) ' HILL average stiffness matrix'
      write(11,2) ((css2(i,j),j=1,6),i=1,6)
      call invten(css2,sss2)
      write(11,*)
      write(11,*) ' HILL average compliance matrix'
      write(11,2) ((sss2(i,j),j=1,6),i=1,6)
      write(11,*)
      write(11,3)
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE cr_to_sa(ng1,ng2,iopt)
c **********************************************************************
c *** Rotates MATERIAL properties from crystal to sample for grains  ***
c *** ng1 to ng2                                                     ***
c *** Option: 0 Rotates Schmid tensors & thermal coefficients        ***
c ***         1 Rotates the stiffness and compliance                 ***
c **********************************************************************
c *** USES:    voigt                                                 ***
c **********************************************************************
c *** VERSION: 12/aug/98                                             ***
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Array dimensions:                                              ***
      DIMENSION ccc4(3,3,3,3),scc4(3,3,3,3),alfacc2(3,3)
      DIMENSION x1(6),x2(3,3),x3(6,6),x4(3,3,3,3)
c ______________________________________________________________________
c
c *** Rotates Schmid tensor, thermal tensor, Burgers vector from CR-->SA
      if (iopt.eq.0) then
c
c *** Rotation of Schmid tensor
         do ng=ng1,ng2
            do i=1,nph
               if (ng.gt.ngrph(i-1)) iph=i
            enddo
            do ns=1,nsys(iph)
               do ij=1,6
                  mcs(ij,ns,ng)=0.d0
                  i=ijv(ij,1)
                  j=ijv(ij,2)
                  do i1=1,3
                     do j1=1,3
                        mcs(ij,ns,ng)=mcs(ij,ns,ng)
     #                       +r(i1,i,ng)*r(j1,j,ng)*mc2(i1,j1,ns,iph)
                     enddo
                  enddo
               enddo
            enddo
         enddo
c
c *** Burgers vector BCS(i,ns,ng) required for twinning reorientation
         do ng=ng1,ng2
            do i=1,nph
               if (ng.gt.ngrph(i-1)) iph=i
            enddo
            do ns=1,nsys(iph)
               do i=1,3
                  bcs(i,ns,ng)=0.d0
                  do j=1,3
                     bcs(i,ns,ng)=bcs(i,ns,ng)+r(j,i,ng)*bcc(j,ns,iph)
                  enddo
               enddo
            enddo
         enddo
c     
c *** Go from 6-vector to 3x3 tensor and rotate thermal expansion tensor
         do i=1,6
            alfacc(i) = alfaccph(i,iph)
         enddo
         call voigt(alfacc,alfacc2,x3,x4,1)
         do ng=ng1,ng2
            do i=1,nph
               if (ng.gt.ngrph(i-1)) iph=i
            enddo
            do ij=1,6
               i=ijv(ij,1)
               j=ijv(ij,2)
               alfacs(ij,ng)=0.d0
               do i1=1,3
                  do j1=1,3
                     alfacs(ij,ng)=alfacs(ij,ng)
     #                    +r(i1,i,ng)*r(j1,j,ng)*alfacc2(i1,j1)
                  enddo
               enddo
            enddo
         enddo
c     
      else
c
c *** Go from (6x6) matrix to (3x3x3x3) tensor and rotate elastic moduli
         iphx=0
         do ng=ng1,ng2
            do i=1,nph
               if (ng.gt.ngrph(i-1)) iph=i
            enddo
            if (iph.ne.iphx) THEN
               do i=1,6
                  do j=1,6
                     ccc2(i,j) = ccc2ph(i,j,iph)
                     scc2(i,j) = scc2ph(i,j,iph)
                  enddo
               enddo
               call voigt(x1,x2,ccc2,ccc4,3)
               call voigt(x1,x2,scc2,scc4,3)
               iphx=iph
            endif
            do ij=1,6
               i=ijv(ij,1)
               j=ijv(ij,2)
               do kl=1,6
                  k=ijv(kl,1)
                  l=ijv(kl,2)
                  ccs2(ij,kl,ng)=0.d0
                  scs2(ij,kl,ng)=0.d0
                  do i1=1,3
                     do j1=1,3
                        do k1=1,3
                           do l1=1,3
                              ccs2(ij,kl,ng)=ccs2(ij,kl,ng)+r(i1,i,ng)
     #                             *r(j1,j,ng)*r(k1,k,ng)
     #                             *r(l1,l,ng)*ccc4(i1,j1,k1,l1)
                              scs2(ij,kl,ng)=scs2(ij,kl,ng)+r(i1,i,ng)
     #                             *r(j1,j,ng)*r(k1,k,ng)
     #                             *r(l1,l,ng)*scc4(i1,j1,k1,l1)
                           enddo
                        enddo
                     enddo
                  enddo
               enddo
            enddo
         enddo
c     
      endif
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE data_material(filemate)
c **********************************************************************
c *** Reads from the file "filemate" the MATERIAL data               ***
c *** Calc. the Schmid tensors                                       ***
c **********************************************************************
c *** USES:    invten                                                ***
c **********************************************************************
c *** VERSION: 13/FEB/98                                             ***
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Variables types definitions                                    ***
      CHARACTER*78 prosa,filemate(NPHX)*40,filetemp*40,namesys*7
      REAL*8 n
      INTEGER b4
c ______________________________________________________________________
c
c *** Array dimension                                                ***
      DIMENSION itypsys(NMOD),hx(NMOD,NMOD),self_hx(NMOD)
      DIMENSION n4(4),b4(4),n(3),b(3)
c ______________________________________________________________________
c
c *** Read and write formats:                                        ***
    1 FORMAT(a)
    2 FORMAT(1h ,78('*'))
    3 FORMAT(1h ,7('*'),' MATERIAL data - File: ',a,8('*'))
    4 FORMAT(1h ,6d12.4)
    5 FORMAT(1h ,'Plastic system modes: ',i3)
    6 FORMAT(1h ,a,2(2x,i3),(2x,d10.4),/1h ,4(2x,d10.4),/1h ,8d11.4)
    7 FORMAT(a4,2x,4i3,3x,4i3)
    8 FORMAT(1h ,a4,2x,4i3,3x,4i3)
    9 FORMAT(a4,1x,3f3.0,6x,3f3.0)
   10 FORMAT(1h ,a4,1x,3f3.0,6x,3f3.0)
   12 FORMAT(1h ,a)
c ______________________________________________________________________
c
c *** LOOP over phases                                               ***
      do iph=1,nph
c ______________________________________________________________________
c
c *** Opens the file with the MATERIAL data "filemate"               ***
         filetemp=filemate(iph)
         OPEN(unit=1,file=filetemp,status='old')
c ______________________________________________________________________
c
         write(11,3) filemate(iph)
         write(11,2)
c ______________________________________________________________________
c
c *** Starts the read/write operation                                ***
         read(1,1) prosa
         write(11,12) prosa
         read(1,1) prosa
         write(11,12) prosa
         read(1,*) ihcp(iph),rca(iph)
         write(11,*) ihcp(iph),rca(iph)
         read(1,1) prosa
         write(11,12) prosa
         do i=1,6
            read(1,*) (ccc2(i,j),j=1,6)
         enddo
         write(11,4) ((ccc2(i,j),j=1,6),i=1,6)
c
c *** Calc. the elastic compliance matrix                            ***
         call invten(ccc2,scc2)
         do i=1,6
            do j=1,6
               ccc2ph(i,j,iph) = ccc2(i,j)
               scc2ph(i,j,iph) = scc2(i,j)
            enddo
         enddo
c     
c *** Skips the lines that are related with the creep properties     ***
         read(1,*)
         read(1,*)
         read(1,*) modrep
         if (modrep.eq.1) then
            read(1,*)
         else
            do i=1,6
               read(1,*)
            enddo
         endif
c
c *** Read the thermal coefficients                                  ***
         read(1,1) prosa
         write(11,12) prosa
         read(1,*) (alfacc(i),i=1,6)
         write(11,4) alfacc
         do i=1,6
            alfaccph(i,iph) = alfacc(i)
         enddo

c
c *** Skips the lines related with growth properties                 ***
         read(1,*)
         read(1,*)
c     
c *** Slip and twinning modes                                        ***
         read(1,1) prosa
         read(1,*) ntotmod
         read(1,1) prosa
         read(1,*) nmodes(iph)
         write(11,5) nmodes(iph)
         if (nmodes(iph).gt.NMOD) then
            write(*,'(1h ,''ERROR: Number of plastic modes greater than
     #           code dimension !!!'',/,1h ,''DIMENSION in code = '',
     #           i3)') NMOD
            write(*,*)
            write(*,'(1h ,''STOP IN ROUTINE *** data_material ***'')')
            read(*,*)
            stop
         endif
         read(1,1) prosa
         read(1,*) (itypsys(i),i=1,nmodes(iph))
         read(1,*) prosa
         im=1
         isys=0
         ntwsys=0
         iloop=1
         do while(iloop.le.ntotmod)
            if (iloop.eq.itypsys(im)) then
               read(1,1) namesys
               read(1,*) nsm(im,iph),itw(im,iph),stw(im,iph)
               read(1,*) tau0x,tau1x,thet0x,thet1x
               if(itw(im,iph).eq.1) read(1,*) twvol,gamdthres,tauprop
               read(1,*) self_hx(im),(hx(im,j),j=1,nmodes(iph))
c     
               if(itw(im,iph).eq.1) ntwsys=ntwsys+nsm(im,iph)
c
c   Slope THETA0 has to be larger or equal to THETA1.
               if(thet0x.lt.thet1x) then
                  write(*,'('' INITIAL HARDENING LOWER THAN FINAL 
     #                 HARDENING'','' FOR MODE'',I3)') im
                  read(*,*)
                  stop
               endif
c   Final slope THETA1 cannot be zero because it gives singular matrix X
               if(thet1x.lt.1.d-3*tau0x) thet1x=1.d-3*tau0x
c   TAU1=0 corresponds to linear hardening with slope THETA1
               if(tau1x.lt.1.d-3*tau0x) then
                  tau1x=0.d0
                  thet0x=thet1x
               endif

               write(11,6) namesys,nsm(im,iph),itw(im,iph),stw(im,iph),
     #              tau0x,tau1x,thet0x,thet1x,
     #              self_hx(im),(hx(im,j),j=1,nmodes(iph))

               do is=1,nsm(im,iph)
                  isys=isys+1
c
c *** If "ihcp = 1" the MATERIAL is "hcp" and reads 4-index notation
c *** If "ihcp = 0" the MATERIAL is "fcc" and reads 3-index notation
                  if (ihcp(iph).eq.1) then
                     read(1,7)   syst(isys),(n4(j),j=1,4),(b4(j),j=1,4)
                     write(11,8) syst(isys),(n4(j),j=1,4),(b4(j),j=1,4)
                     n(1)=n4(1)
                     n(2)=(n4(1)+2.d0*n4(2))/dsqrt(3.d0)
                     n(3)=n4(4)/rca(iph)
                     b(1)=3.d0/2.d0*b4(1)
                     b(2)=(b4(1)/2.d0+b4(2))*dsqrt(3.d0)
                     b(3)=b4(4)*rca(iph)
                  else
                     read(1,9)    syst(isys),(n(j),j=1,3),(b(j),j=1,3)
                     write(11,10) syst(isys),(n(j),j=1,3),(b(j),j=1,3)
                  endif
c *** Normalizes system vecotrs and checks normality.
c *** Array BCC(i) required for twinning reorientation (aug/98)
                  rn=dsqrt(n(1)**2+n(2)**2+n(3)**2)
                  rb=dsqrt(b(1)**2+b(2)**2+b(3)**2)
                  prod=0.d0
                  do j=1,3
                     n(j)=n(j)/rn
                     b(j)=b(j)/rb
                     prod=prod+n(j)*b(j)
                     bcc(j,isys,iph)=b(j)
                  enddo
                  if(prod.ge.1.e-3) then
                     write(*,'(''SYSTEM'',i4,''  IN MODE'',i4,
     #                    ''  IS NOT ORTHOGONAL !!'')') isys,im
                     read(*,*)
                     stop
                  endif
c
c *** Calculates Schmid tensor
                  mc2(1,1,isys,iph)=b(1)*n(1)
                  mc2(2,2,isys,iph)=b(2)*n(2)
                  mc2(3,3,isys,iph)=b(3)*n(3)
                  mc2(2,3,isys,iph)=0.5d0*(b(2)*n(3)+b(3)*n(2))
                  mc2(3,2,isys,iph)=mc2(2,3,isys,iph)
                  mc2(1,3,isys,iph)=0.5d0*(b(1)*n(3)+b(3)*n(1))
                  mc2(3,1,isys,iph)=mc2(1,3,isys,iph)
                  mc2(1,2,isys,iph)=0.5d0*(b(1)*n(2)+b(2)*n(1))
                  mc2(2,1,isys,iph)=mc2(1,2,isys,iph)
c
c *** Assign the parameters to each plastic system                   ***
                  tau0(isys,iph) =tau0x
                  tau1(isys,iph) =tau1x
                  thet0(isys,iph)=thet0x
                  thet1(isys,iph)=thet1x
               enddo            ! end of loop over systems in the mode
c
               if (isys.gt.NSLS) then
                  write(*,'(1h ,
     #                 ''ERROR: Number of systems greater than code'',
     #                 '' dimension !!!'',/,1h ,
     #                 ''Code DIMENSION = '',i3)') NSLS
                  write(*,*)
                  write(*,'(1h ,
     #                 ''STOP IN ROUTINE *** data_material ***'')')
                  read(*,*)
                  stop
               endif
               if (im.gt.NMOD) then
                  write(*,'(1h ,
     #                 ''ERROR: Number of modes greater than code''
     #                 ,'' dimension !!!'',/,1h ,
     #                 ''Code DIMENSION = '',i3)') NMOD
                  write(*,*)
                  write(*,'(1h ,
     #                 ''STOP IN ROUTINE *** data_material ***'')')
                  read(*,*)
                  stop
               endif
               im=im+1
               if (im.gt.nmodes(iph)) iloop=ntotmod
c
            else
               read(1,1) namesys
               read(1,*) nsmx
               read(1,*)
               read(1,*)
               do is=1,nsmx
                  read(1,*)
               enddo
            endif
            iloop=iloop+1
         enddo                  ! end of loop over total number of modes
         nsys(iph)=isys
c
         if(nmodes(iph).eq.1.and.nsys(iph).eq.1) then
           iVM(iph)=1
         else
           iVM(iph)=0
         endif
c
c
c *** Assigns the hardening coefficients to each plastic system      ***
         i=1
         do im=1,nmodes(iph)
            do is=1,nsm(im,iph)
               j=1
               do jm=1,nmodes(iph)
                  do js=1,nsm(jm,iph)
                     h(i,j,iph)=hx(im,jm)
                     j=j+1
                  enddo
               enddo
               h(i,i,iph)=self_hx(im)
               i=i+1
            enddo
         enddo
c
c *** Assigns the opposite hardening coefficient (softening) for the ***
c *** interaction between opposite systems.                          ***
c *** WARNING --> Used for specific study of Bauschinger.
c      do iph=1,nph
c         i=1
c         do im=1,nmodes(iph)
c            if (itw(im,iph).eq.0) then
c               do is=1,nsm(im,iph),2
c                  h(i,i+1)=-hx(im,im)
c                  h(i+1,i)=-hx(im,im)
c                  i=i+2
c               enddo
c            endif
c         enddo
c      enddo
c ______________________________________________________________________
c
         write(11,*)
         write(11,2)
         CLOSE(unit=1)
      enddo                     ! end LOOP over PHASES
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE data_process(fileproc,i_temp_cij,i_et_0,i_control_var)
c **********************************************************************
c *** Reads from the file "fileproc" the PROCESS data                ***
c **********************************************************************
c *** VERSION: 12/OCT/94                                             ***
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Variables types definitions                                    ***
      CHARACTER*78 prosa,fileproc*40
c ______________________________________________________________________
c
c *** Read and write formats:                                        ***
    1 FORMAT(a)
    2 FORMAT(1h ,78('*'))
    3 FORMAT(1h ,8('*'),' PROCESS data - File: ',a,8('*'))
    4 FORMAT(1h ,6(6x,i6))
    5 FORMAT(1h ,6d12.4)
    6 FORMAT(1h ,'ITMAX OVER MODULUS= ',i3,' ERROR= ',d12.4)
    7 FORMAT(1h ,'ITMAX OVER GRAINS= ',i3)
    8 FORMAT(1h ,d12.4)
   12 FORMAT(1h ,a)
c ______________________________________________________________________
c
c *** Opens the file with the PROCESS data "fileproc"                ***
      OPEN(unit=1,file=fileproc,status='old')
c ______________________________________________________________________
c
      write(11,3) fileproc
      write(11,2)
c ______________________________________________________________________
c
c *** Starts the read/write operations                               ***
      read(1,1) prosa
      write(11,12) prosa
      read(1,1) prosa
      write(11,12) prosa
      read(1,*) nsteps
      write(11,*) nsteps
      read(1,1) prosa
      write(11,12) prosa
      read(1,*) temp_s,temp_f
      write(11,*) temp_s,temp_f
      read(1,1) prosa
      write(11,12) prosa
      read(1,*) i_temp_cij
      write(11,*) i_temp_cij
      read(1,1) prosa
      write(11,12) prosa
      read(1,*) (istbc(i),i=1,6)
      write(11,4) (istbc(i),i=1,6)
      read(1,*) (stbc(i),i=1,6)
      write(11,5) (stbc(i),i=1,6)
      read(1,1) prosa
      write(11,12) prosa
      read(1,*) (ietbc(i),i=1,6)
      write(11,4) (ietbc(i),i=1,6)
      read(1,*) (etbc(i),i=1,6)
      write(11,5) (etbc(i),i=1,6)
      read(1,1) prosa
      write(11,12) prosa
      read(1,*) i_et_0
      write(11,*) i_et_0
      read(1,1) prosa
      write(11,12) prosa
      read(1,*) i_control_var
      write(11,*) i_control_var
      read(1,1) prosa
      write(11,12) prosa
      read(1,*) itmax_mod,error_mod
      write(11,6) itmax_mod,error_mod
      read(1,1) prosa
      write(11,12) prosa
      read(1,*) itmax_grain
      write(11,7) itmax_grain
c ______________________________________________________________________
c
      write(11,*)
      write(11,2)
      CLOSE(unit=1)
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE data_sample(filesamp,i_prev_proc,fileprev)
c **********************************************************************
c *** Reads from the file "filesamp" the SAMPLE data                 ***
c *** Renormalize the weights and calculate the rotation matrix for  ***
c *** each grain in the sample                                       ***
c **********************************************************************
c *** USES:    euler                                                 ***
c **********************************************************************
c *** VERSION: 11/aug/98                                             ***
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Variables types definitions:                                   ***
      CHARACTER*78 prosa,fileprev*40,eul_conv*1
      CHARACTER*40 filetemp,filesamp(NPHX)
c ______________________________________________________________________
c
c *** Array dimension:                                               ***
      DIMENSION text2(3),text4(3),aux33(3,3)
c ______________________________________________________________________
c
c *** Read and write formats:                                        ***
    1 FORMAT(a)
    2 FORMAT(1h ,78('*'))
    3 FORMAT(1h ,8('*'),' SAMPLE data - File: ',a,9('*'))
    4 FORMAT(1h ,3f7.2)
    5 FORMAT(1h ,'Texture coefficients for crystal axis 3:')
    6 FORMAT(1h ,'  Second order: ',3f12.5)
    7 FORMAT(1h ,'  Fourth order: ',3f12.5)
    8 FORMAT(1h ,'The texture may be written in "EPSC2.OUT"')
    9 FORMAT(1h ,i5,4f12.5)
   10 FORMAT(a1,2i5)
   11 FORMAT(1h ,a1,2i5)
   12 FORMAT(1h ,a)
c ______________________________________________________________________
c
      ngrain=0
      ngrph(0)=0
c *** LOOP over phases                                               ***
      do iph=1,nph
c ______________________________________________________________________
c
c *** Opens the file with the SAMPLE data "filesamp"                 ***
         filetemp=filesamp(iph)
         OPEN(unit=1,file=filetemp,status='old')
c ______________________________________________________________________
c
         do iunit=11,12
            write(iunit,3) filetemp
            write(iunit,2)
         enddo
c ______________________________________________________________________
c
c *** Start the read/write operation:                                ***
         read(1,1) prosa
         write(11,12) prosa
         write(12,12) prosa
         read(1,*) axis
         write(11,4) axis
         do i=1,3
            axisph(i,iph)=axis(i)
         enddo
         read(1,1) prosa
         write(11,12) prosa
         write(12,12) prosa
         read(1,*) eul_conv,ngrph(iph),ngrprn
c     Renormalizing the phase volume fractions with the numbr of grains within the phase
         wph(iph)=wph(iph)/ngrph(iph)
c
         ngrain = ngrain + ngrph(iph)
         ngrph(iph) = ngrph(iph) + ngrph(iph-1)
c         write(*,*) 'Number of grains is : ',ngrain
c         read(*,*)
         if (ngrain.gt.NGR) then
            write(*,'(1h ,''ERROR: Number of grains greater than code''
     #           ,'' dimension !!!'',/,1h ,''DIMENSION in code = '',
     #           i3)') NGR
            write(*,*)
            write(*,'(1h ,''STOP IN ROUTINE *** data_sample ***'')')
            read(*,*)
            stop
         endif
         write(11,11) eul_conv,ngrph(iph),ngrprn
         write(12,11) eul_conv,ngrph(iph),ngrprn
         write(11,8)
         read(1,*) (phi(i),the(i),ome(i),wgt(i),
     #        i=1+ngrph(iph-1),ngrph(iph))
c
c     print *
c     print *, 'RANDOM SHIFT OF EULER ANGLES WITHIN 3 degs ACTIVATED'
c     print *, 'TO AVOID FULLY SYMMETRIC ORIENTATIONS'
c     print *
c     jran=-1
c      do i=1,ngrain
c        phi(i)= phi(i)+ran2(jran)*3.
c        the(i)= the(i)+ran2(jran)*3.
c        ome(i)= ome(i)+ran2(jran)*3.
c      enddo
c
c     write(12,9) (i,phi(i),the(i),ome(i),wgt(i),i=1,ngrain)
c
         close(unit=1)
c ______________________________________________________________________
c
      enddo                     ! end of LOOP over phases
c ______________________________________________________________________
c
c *** Calc. rotation matrix for each grain                           ***
c *** The matrix r(i,j,ngr) transforms from sample to crystal        ***
      totwgt=0.d0
      do iph=1,nph
         do ng=1+ngrph(iph-1),ngrph(iph)
            totwgt=totwgt+wgt(ng)*wph(iph)
         enddo
      enddo
      do i=1,3
         text2(i)=0.d0
         text4(i)=0.d0
      enddo
      do iph=1,nph
         do ng=1+ngrph(iph-1),ngrph(iph)
            call euler(2,phi(ng),the(ng),ome(ng),aux33)
            wgt(ng)=wgt(ng)*wph(iph)/totwgt
            do i=1,3
               text2(i)=text2(i)+aux33(3,i)**2*wgt(ng)
               text4(i)=text4(i)+aux33(3,i)**4*wgt(ng)
               do j=1,3
                  r(i,j,ng)=aux33(i,j)
               enddo
            enddo
         enddo
      enddo
      write(12,5)
      write(12,6) text2
      write(12,7) text4
      write(12,*)
c ______________________________________________________________________
c
c *** Reads the data from the previous procedure if i_prev_proc=1    ***
c ______________________________________________________________________
c
c *** NOT IMPLEMENTED FOR N PHASES YET !!!!!!!!!!!                   ***
c ______________________________________________________________________
      if (i_prev_proc.eq.1) then
         open(unit=1,file=fileprev,status='old')
         do i=1,6
            read(1,1) prosa
         enddo
         read(1,*) ((ass2(i,j),j=1,6),i=1,6)
         read(1,1) prosa
         read(1,*) alfass
         read(1,1) prosa
         read(1,*) stss
         read(1,*) etss
         read(1,*) etelss
         read(1,1) prosa
         do ng=1,ngrain
            read(1,*) (stcs(i,ng),i=1,6)
            read(1,*) (etcs(i,ng),i=1,6)
         enddo
         read(1,1) prosa
         do iph=1,nph
            do ng=1+ngrph(iph-1),ngrph(iph)
               read(1,*) (tau(ns1,ng),ns1=1,nsys(iph)),gamtot(ng)
               do ns1=1,nsys(iph)
                  tau(ns1,ng)=tau(ns1,ng)*tau0(ns1,iph)
               enddo
            enddo
         enddo
      else
c
c *** Assigns critical stresses to each grain and intializes grain arrays
         do iph=1,nph
            do ng=1+ngrph(iph-1),ngrph(iph)
               gamtot(ng)=0.d0
               do ns1=1,nsys(iph)
                  tau(ns1,ng)=tau0(ns1,iph)
               enddo
            enddo
         enddo
         ngrainx=ngrain
         do ng=1,ngrain
            wgtx(ng)=wgt(ng)
         enddo
c     
      endif                     !(i_prev_proc.eq.1)
c ______________________________________________________________________
c
      write(11,*)
      write(11,2)
c
      CLOSE(unit=1)
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE dif_planes(filediff,temp,i_control_var,iopt)
c **********************************************************************
c *** Finds the grains whose planes contribute to a diffraction
c *** direction (iopt=0)
c *** Calculates the weigthed average of the elastic strain across a
c *** family of planes perpendicular to a diffraction direction (iopt=1)
c *** Makes a histogram for the grain stress along such direct (iopt=2)
c **********************************************************************
c *** VERSION 20/APR/95
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      PARAMETER (NFAM=12)
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Variables types definitions:                                   ***
      CHARACTER*78 prosa,filediff(NPHX)*40
c ______________________________________________________________________
c
c *** Array dimensions:                                              ***
      DIMENSION pc(3,NFAM),ps(3),vs(NDIFFX,3),n4(4)
      DIMENSION sintset(NDIFFX),wgtdif(NGR,NDIFFX),v(0:1,NGR)
      DIMENSION residual(6),para_w(NDIFFX,NPHX),para_i(NDIFFX,NPHX)
c ______________________________________________________________________
c
      pi=4.d0*datan(1.d0)
c
c *** Read and write formats:                                        ***
    1 FORMAT(a)
    2 FORMAT(1h ,a)
    3 FORMAT(1h ,i5,f6.2)
    4 FORMAT(1h ,4i3,2(4x,f8.2))
    5 FORMAT(1h ,3i3,3x,2(4x,f8.2))
    6 FORMAT(1h ,'  SET #:',i5,'  NGRSET:',i5,
     #           '  VOLFRAC:',f9.5,'  INTENS: ',f9.5)
    7 FORMAT(1h ,15i5)
    9 FORMAT(1h ,d12.4,3x,9d11.3,/,(16x,9d11.3))
c
c *** Starts the calculation:
c
      if (iopt.eq.0) then
         do iph=1,nph
            if (i_diff_dir(iph).eq.1) then
               OPEN(unit=1,file=filediff(iph),status='old')
               read(1,1) prosa
               write(19,2) prosa
               read(1,1) prosa
               write(19,2) prosa
               read(1,*) ndiff(iph),spread
               write(19,3) ndiff(iph),spread
               if (ndiff(iph).gt.NDIFFX) then
                  write(*,'(1h ,
     #                 ''ERROR: Number of diffraction directions''
     #                 '' greater than code dimension !!!'',/,1h ,
     #                 ''DIMENSION in'''' code = '',i3)') NDIFFX
                  write(*,*)
                  write(*,'(1h ,
     #                 ''STOP IN ROUTINE *** dif_planes ***'')')
                  read(*,*)
                  stop
               endif
               do n=1,ndiff(iph)
                  para_w(n,iph)=0.d0
                  para_i(n,iph)=0.d0
               enddo
               toler=dcos(spread*pi/180.d0)
               read(1,1) prosa
               write(19,2) prosa
               read(1,1) prosa
               write(19,2) prosa
               prosa=prosa      ! only to fool the compiler
c
c *** Checks for the grains in each diffraction direction            ***
               do n=1,ndiff(iph)
                  if (ihcp(iph).eq.1) then
                     read(1,*) (n4(i),i=1,4),angle_chi,angle_eta
                     write(19,4) (n4(i),i=1,4),angle_chi,angle_eta
                  else
                     read(1,*) (n4(i),i=1,3),angle_chi,angle_eta
                     write(19,5) (n4(i),i=1,3),angle_chi,angle_eta
                  endif
                  angle_chi=angle_chi*pi/180.d0
                  angle_eta=angle_eta*pi/180.d0
                  vs(n,1)=dcos(angle_eta)*dsin(angle_chi)
                  vs(n,2)=dsin(angle_eta)*dsin(angle_chi)
                  vs(n,3)=dcos(angle_chi)
c
                  call equiv_planes(ihcp(iph),rca(iph),n4,pc,nfamily)
c
                  ngrset(n,iph)=0
                  wgtset(n,iph)=0.d0
                  sintset(n)=0.d0
                  do ng=1+ngrph(iph-1),ngrph(iph)
                     do ipl=1,nfamily
                        do i=1,3
                           ps(i)=0.d0
                           do j=1,3
                              ps(i)=ps(i)+r(j,i,ng)*pc(j,ipl)
                           enddo
                        enddo
                        prodesc=0.d0
                        do i=1,3
                           prodesc=prodesc+ps(i)*vs(n,i)
                        enddo
                        if (dabs(prodesc).ge.toler) then
                           ngrset(n,iph)=ngrset(n,iph)+1
                           igrset(n,ngrset(n,iph),iph)=ng
                           wgtdif(ng,n)=wgtx(ng)*dabs(prodesc)
                           wgtset(n,iph)=wgtset(n,iph)+wgtdif(ng,n)
                           if (the(ng).ne.0.d0) then
                              sintset(n)=sintset(n)+wgtdif(ng,n)
     #                             /dabs(dsin(the(ng)*pi/180.d0))
                           endif
                        endif
                     enddo
                  enddo
               enddo
c
               iprint=1
               if(iprint.eq.1) then
                  do n=1,ndiff(iph)
                     write(19,*)
                     write(19,6) n,ngrset(n,iph),wgtset(n,iph),
     #                    sintset(n)
                     write(19,7) (igrset(n,n1,iph),n1=1,ngrset(n,iph))
                  enddo
                  write(19,*)
                  write(19,'('' CONTROL VARIABLE & AVERAGE ELASTIC '',
     #                 ''STRAIN IN  DIFFRACTING PLANES (NORMALIZED '',
     #                 ''WITH WEIGHTS)'')')
               endif
c
               CLOSE(unit=1)
            endif
         enddo
        write(19,'($3(2x,a))') 'control   ','eps33     ','sig33     '
        do iph=1,nph
          if (i_diff_dir(iph).eq.1) then
            do nd=1,ndiff(iph)
              write(19,"($2x,a,I1.1,a,I3.3,a)") 'ph',iph,'ref',nd,' '
            enddo
          endif
        enddo
        write(19,*)
c
      endif                     ! END OF IOPTION=0
c
c *** calculates the average strain for a crystallographic family along
c *** the diffraction direction.
c *** See line 400'ish for comment on stcdref:
c *** A modification by CNT on 15/07/98 permits to refer 'elastic' strain
c *** in grains to the values of the previous process (for comparing with
c *** X-ray or neutron measurements).
c
      if (iopt.eq.1) then
c
         do iph=1,nph
            if (i_diff_dir(iph).eq.1) then
               do n=1,ndiff(iph)
                  para_w(n,iph)=0.d0
                  para_i(n,iph)=0.d0
                  do ng=1,ngrset(n,iph)
                     ngset=igrset(n,ng,iph)
                     eps=0.d0
                     do i=1,6
                        residual(i)=0.d0
                        do j=1,6
                           residual(i)=residual(i)+scs2(i,j,ngset)*
     #                          (stcs(j,ngset)-stcsref(j,ngset))*
     #                          profac(j)
                        enddo
                     enddo
                     do ij=1,6
                        i=ijv(ij,1)
                        j=ijv(ij,2)
                        eps=eps+residual(ij)*vs(n,i)*vs(n,j)*profac(ij)
                     enddo
                     para_w(n,iph)=para_w(n,iph)+eps*wgtdif(ngset,n)
                     if (the(ngset).ne.0.) para_i(n,iph)=para_i(n,iph)+
     #                    eps*wgtdif(ngset,n)/
     #                    dabs(dsin(the(ngset)*pi/180.d0))
                  enddo
                  if(wgtset(n,iph).ne.0.d0)  para_w(n,iph)=
     #                 para_w(n,iph)/wgtset(n,iph)
                  if(sintset(n).ne.0.d0) para_i(n,nph)=
     #                 para_i(n,iph)/sintset(n)
c
c **********************************************************************
c *** activate the next block if refering internal strains to av. el. strain
c          eps=0
c          do ij=1,6
c            i=ijv(ij,1)
c            j=ijv(ij,2)
c            eps=eps+etelss(ij)*vs(n,i)*vs(n,j)*profac(ij)
c          enddo
c          para_w(n)=para_w(n)-eps
c          para_i(n)=para_i(n)-eps
c **********************************************************************
c
               enddo
            endif
         enddo                  ! END OF LOOP OVER DIFFRACTING PLANES
c     
c *** Write the results in "EPSC9.OUT" -> unit=19                    ***
         if (i_control_var.eq.0) xref=temp
         if (i_control_var.ge.1) xref=etss(i_control_var)
         if (i_control_var.ge.4) xref=stss(i_control_var-3)
c
c
c **********************************************************************
c *** Standard output of average strain in diffracting planes.
c
c        write(19,*) 'STRAIN ACROSS ndiff PLANES (normalized w/weight)'
c        write(19,9) xref,(para_w(n,iph),n=1,ndiff(iph))
c        write(20,9) xref,(wgtset(n,iph),n=1,ndiff(iph))
c        write(19,*) 'STRAIN ACROSS ndiff PLANES (normalized w/intens)'
c        write(19,9) xref,(para_i(n,iph),n=1,ndiff(iph))
c        write(20,9) xref,(sintset(n),n=1,ndiff(iph))
c
c *************************************************************************
c *** Inconel-600 calculations
c *** Specific output for (ijk) along rim RD-TD-ND every 5 degrees.
c
c      write(19,'(i5,f10.6)')
c    #           (5*(iang-1),para_w(iang,iph),iang=1,55)
c
c *** Specific output for (ijk) pole figure in first quad. every 15 degrees.
c
c      write(19,'(i5,7f10.6)')
c    #      (15*(ieta-1),(para_w(ieta+7*(ichi-1),iph),ichi=1,7),ieta=1,7)
c
c *** Specific output for (001),(110),(111) every 10 degrees betw. ND & RD
c
c       write(19,'(i5,4f10.6)') (10*(iang-1),sin(10*(iang-1)*pi/180.)**2,
c     # para_w(iang,iph),para_w(iang+10,iph),para_w(iang+20,iph),iang=1,10)
c
c *************************************************************************
c *** Specific output for random Be along compression direction and along
c *** both transverse directions averaged.
c
c      xref=xref      ! only to fool the compiler
c      ixx=i_control_var
c      write(19,'(2f10.4,3x,18d11.3)') etss(ixx),stss(ixx),
c    #    (para_w(n),n=1,9),((para_w(n+9)+para_w(n+18))/2.,n=1,9)
c      write(20,'(2f10.4,3x,18d11.3)') etss(ixx),stss(ixx),
c    #       (wgtset(n,iph),n=1,9),
c    #       ((wgtset(n+9,iph)+wgtset(n+18,iph))/2.,n=1,9)
c
c *************************************************************************
c *** Specific output for (111) (110) (100) (113), each along ND-RD, TD-RD,
c *** TD-ND planes every 15 degrees.
c
c      ixx=i_control_var
c      write(19,'(5x,f10.4,10x,f10.4)') etss(ixx),stss(ixx)
c      write(19,10) (15*(iang-1),(para_w(iang+7*(n-1),iph),n=1,12),iang=1,7)
c  10  format(i5,12f10.6)
c
c *************************************************************************
c *** Specific output for (111) (100), each along RD-TD every 10 degrees.
c
c      ixx=i_control_var
c      write(19,'(5x,f10.4,10x,f10.4)') etss(ixx),stss(ixx)
c      write(19,'(i5,2f10.6)')
c    #           (10*(iang-1),(para_w(iang+10*(n-1),iph),n=1,2),iang=1,10)
c
c *************************************************************************
c *** Specific output for FCC reflections (111) (200) (220) (311) (331)
c *** Specific output for BCC reflections (110) (200) (211) (310) (222)
c *** Each along RD,TD & ND.
c
c         write(19,'(E11.3,0x,300E11.3)') 
c    #        xref,((para_w(nd,iph),nd=1,ndiff(iph)),iph=1,2)
c
	    write(19,'($3(E12.4,0x))') xref,etss(3),stss(3)
          do iph=1,nph
            if (i_diff_dir(iph).eq.1) then
              write(19,'($12E12.4)')(para_w(nd,iph),nd=1,ndiff(iph))
            endif
          enddo
          write(19,*)
c
c
c *************************************************************************
      endif                     !END OF IOPTION=1
c     
c *** performs a statistic for the stress comp. normal to the dif. planes
c
      if (iopt.eq.2) then
         do iph=1,nph
            if (i_diff_dir(iph).eq.1) then
               do n=1,ndiff(iph)
                  do ng=1,ngrset(n,iph)
                     ngset=igrset(n,ng,iph)
                     sig=0.d0
                     do ij=1,6
                        i=ijv(ij,1)
                        j=ijv(ij,2)
                        sig=sig+vs(n,i)*vs(n,j)*stcs(ij,ngset)*
     #                       profac(ij)
                     enddo
                     v(0,ng)=wgtx(ngset)
                     v(1,ng)=sig
                  enddo
c
                  print *
                  print *, '----> SKIPS STRESS HISTOGRAM FOR 
     #                 EACH DIFFRACTING PLANE'
                  call histogram (v,1,ngrset(n,iph),19)
               enddo
            endif
         enddo
      endif                     !END OF IOPTION=2
c
c
c
      if (iopt.eq.3) then
         do iph=1,nph
            if (i_diff_dir(iph).eq.1.and.ntwsys(iph).ne.0) then
               OPEN(unit=1,file=filediff(iph),status='old')
               read(1,1) prosa
               write(19,2) prosa
               read(1,1) prosa
               write(19,2) prosa
               read(1,*) ndiff(iph),spread
               write(19,3) ndiff(iph),spread
               if (ndiff(iph).gt.NDIFFX) then
                  write(*,'(1h ,
     #                 ''ERROR: Number of diffraction directions''
     #                 '' greater than code dimension !!!'',/,1h ,
     #                 ''DIMENSION in'''' code = '',i3)') NDIFFX
                  write(*,*)
                  write(*,'(1h ,
     #                 ''STOP IN ROUTINE *** dif_planes ***'')')
                  read(*,*)
                  stop
               endif
               toler=dcos(spread*pi/180.d0)
               read(1,1) prosa
               write(19,2) prosa
               read(1,1) prosa
               write(19,2) prosa
               prosa=prosa      ! only to fool the compiler
c
c *** Checks for the grains in each diffraction direction            ***
               do n=1,ndiff(iph)
                  if (ihcp(iph).eq.1) then
                     read(1,*) (n4(i),i=1,4),angle_chi,angle_eta
                     write(19,4) (n4(i),i=1,4),angle_chi,angle_eta
                  else
                     read(1,*) (n4(i),i=1,3),angle_chi,angle_eta
                     write(19,5) (n4(i),i=1,3),angle_chi,angle_eta
                  endif
                  angle_chi=angle_chi*pi/180.d0
                  angle_eta=angle_eta*pi/180.d0
                  vs(n,1)=dcos(angle_eta)*dsin(angle_chi)
                  vs(n,2)=dsin(angle_eta)*dsin(angle_chi)
                  vs(n,3)=dcos(angle_chi)
c
                  call equiv_planes(ihcp(iph),rca(iph),n4,pc,nfamily)
c
                  ngrset(n,iph)=0
                  wgtset(n,iph)=0.d0
                  sintset(n)=0.d0
                  do ng=1,ngrainx
                     do ipl=1,nfamily
                        do i=1,3
                           ps(i)=0.d0
                           do j=1,3
                              ps(i)=ps(i)+r(j,i,ng)*pc(j,ipl)
                           enddo
                        enddo
                        prodesc=0.d0
                        do i=1,3
                           prodesc=prodesc+ps(i)*vs(n,i)
                        enddo
                        if (dabs(prodesc).ge.toler) then
                           ngrset(n,iph)=ngrset(n,iph)+1
                           igrset(n,ngrset(n,iph),iph)=ng
                           wgtdif(ng,n)=wgtx(ng)*dabs(prodesc)
                           wgtset(n,iph)=wgtset(n,iph)+wgtdif(ng,n)
                           if (the(ng).ne.0.d0) then
                              sintset(n)=sintset(n)+wgtdif(ng,n)
     #                             /dabs(dsin(the(ng)*pi/180.d0))
                           endif
                        endif
                     enddo
                  enddo
               enddo
c
               iprint=1
               if(iprint.eq.1) then
                  do n=1,ndiff(iph)
                     write(19,*)
                     write(19,6) n,ngrset(n,iph),wgtset(n,iph),
     #                    sintset(n)
                     write(19,7) (igrset(n,n1,iph),n1=1,ngrset(n,iph))
                  enddo
                  write(19,*)
                  write(19,'('' CONTROL VARIABLE & AVERAGE STRAIN IN'',
     #            '' DIFFRACTING PLANES (NORMALIZED WITH WEIGHTS)'')')
               endif
c
               CLOSE(unit=1)
            endif
         enddo
      endif                     !END OF OPTION 3
c
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE equiv_planes(ihcp,rca,n4,pc,nfamily)
c **********************************************************************
c *** For a given crystal symmetry, finds the family of equivalent   ***
c *** planes to the one defined by the indices n4(i).
c **********************************************************************
c *** VERSION 20/APR/95                                              ***
c **********************************************************************
      IMPLICIT REAL*8 (a-h,o-z)
c ______________________________________________________________________
c
c *** Array dimensions:                                              ***
      DIMENSION pc(3,12),n4(4),itag(12)
c ______________________________________________________________________
c
c *** Calculation for cubic symmetry: 12 equivalent planes (there may be
c *** redundancies) obtained from n4(i) by index permutation + sign
c *** permutation. The third component is always defined positive.
c *** Opposite directions are not required.
c
      if (ihcp.eq.0) then
        n=1
        do ip=1,3
          ip1= ip   - ip   /4*3
          ip2=(ip+1)-(ip+1)/4*3
          ip3=(ip+2)-(ip+2)/4*3
          pc(1,n)= n4(ip1)
          pc(2,n)= n4(ip2)
          pc(3,n)= n4(ip3)
          n=n+1
          pc(1,n)=-n4(ip1)
          pc(2,n)= n4(ip2)
          pc(3,n)= n4(ip3)
          n=n+1
          pc(1,n)= n4(ip1)
          pc(2,n)=-n4(ip2)
          pc(3,n)= n4(ip3)
          n=n+1
          pc(1,n)=-n4(ip1)
          pc(2,n)=-n4(ip2)
          pc(3,n)= n4(ip3)
          n=n+1
        enddo
        nfamily=n-1
      endif
c
c *** Calculation for hexagonal symmetry: 6 equivalent planes (there may be
c *** redundancies) obtained from n4(i) by index permutation of the first
c *** three indices, followed by sign inversion of the basal component.
c *** The c-axis component is kept positive. Opposite directions superfluous.
c
      if (ihcp.eq.1) then
        nfamily=6
        do ip=1,3
          ip1= ip   - ip   /4*3
          ip2=(ip+1)-(ip+1)/4*3
          pc(1,ip)= n4(ip1)
          pc(2,ip)=(n4(ip1)+2.d0*n4(ip2))/dsqrt(3.d0)
          pc(3,ip)= n4(4)/rca
          pc(1,ip+3)=-pc(1,ip)
          pc(2,ip+3)=-pc(2,ip)
          pc(3,ip+3)= pc(3,ip)
        enddo
      endif
c
      do nf=1,nfamily
        itag(nf)=0
        pcn=dsqrt(pc(1,nf)**2+pc(2,nf)**2+pc(3,nf)**2)
        do j=1,3
          pc(j,nf)=pc(j,nf)/pcn
        enddo
      enddo
c
c *** tags and eliminates the redundant (repeated) planes from the family.
c
      do nf=1,nfamily-1
        do mf=nf+1,nfamily
          pcdif=(pc(1,nf)-pc(1,mf))**2+(pc(2,nf)-pc(2,mf))**2+
     #          (pc(3,nf)-pc(3,mf))**2
          pcsum=(pc(1,nf)+pc(1,mf))**2+(pc(2,nf)+pc(2,mf))**2+
     #          (pc(3,nf)+pc(3,mf))**2
          if(pcdif.le.1.d-4 .or. pcsum.le.1.d-4) itag(mf)=1
        enddo
      enddo
c
      nfax=0
      do nf=1,nfamily
        if(itag(nf).eq.0) then
          nfax=nfax+1
          pc(1,nfax)=pc(1,nf)
          pc(2,nfax)=pc(2,nf)
          pc(3,nfax)=pc(3,nf)
        endif
      enddo
      nfamily=nfax
c
c      write(19,*) 'family of diffracting planes'
c      write(19,'(3f8.3)') ((pc(i,nf),i=1,3),nf=1,nfamily)
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE EULER(IOPT,PH,TH,OM,A)
C **********************************************************************
C *** THIS SUBROUTINE CALCULATES THE EULER ANGLES ASSOCIATED WITH THE***
C *** TRANSFORMATION MATRIX A(I,J) IF IOPT=1 AND VICEVERSA IF IOPT=2 ***
C ***                                                                ***
C *** A(I,J) TRANSFORMS FROM SYSTEM A TO SYSTEM B IF PH,TH,OM ARE THE***
C *** EULER ANGLES THAT THE DESCRIBE THE SEQUENCE OF ROTATIONS OF THE***
C *** SYSTEM B WITH RESPECT TO SYSTEM A.                             ***
c **********************************************************************
c *** VERSION: 10/AUG/98                                             ***
c **********************************************************************
      IMPLICIT REAL*8 (A-H,O-Z)
      DIMENSION A(3,3)
      PI=4.D0*DATAN(1.D0)
C
      GO TO(5,20),IOPT
    5 TH=DACOS(A(3,3))
      IF(DABS(A(3,3)).GE.0.9999) GO TO 10
      STH=DSIN(TH)
      OM=DATAN2(A(1,3)/STH,A(2,3)/STH)
      PH=DATAN2(A(3,1)/STH,-A(3,2)/STH)
      GO TO 15
   10 OM=0.0D0
      PH=DATAN2(A(1,2),A(1,1))
   15 CONTINUE
      TH= TH*180.0D0/PI
      PH= PH*180.0D0/PI
      OM= OM*180.0D0/PI
      RETURN
C
   20 SPH=DSIN(PH*PI/180.D0)
      CPH=DCOS(PH*PI/180.D0)
      STH=DSIN(TH*PI/180.D0)
      CTH=DCOS(TH*PI/180.D0)
      SOM=DSIN(OM*PI/180.D0)
      COM=DCOS(OM*PI/180.D0)
      A(1,1)= COM*CPH-SPH*SOM*CTH
      A(2,1)=-SOM*CPH-SPH*COM*CTH
      A(3,1)= SPH*STH
      A(1,2)= COM*SPH+CPH*SOM*CTH
      A(2,2)=-SPH*SOM+CPH*COM*CTH
      A(3,2)=-STH*CPH
      A(1,3)= STH*SOM
      A(2,3)= COM*STH
      A(3,3)= CTH
      RETURN
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE g_actsys(nout_old)
c **********************************************************************
c *** Evaluates the active slip systems in each grain                ***
c *** Modify the critical stress if the stress state is out of SCYS  ***
c **********************************************************************
c *** VERSION: 12/OCT/94                                             ***
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
      REAL J2
      DIMENSION s(6)
c ______________________________________________________________________
c
      nout=0
      do iph=1,nph
       if(iVM(iph).eq.0) then
         do ng=1+ngrph(iph-1),ngrph(iph)
            nout_flag=0
            nact(ng)=0
            do ns1=1,nsys(iph)
               rss=0.d0
               do i=1,6
                  rss=rss+mcs(i,ns1,ng)*stcs(i,ng)*profac(i)
               enddo
               rss=rss/tau(ns1,ng)
               if (rss.ge.0.98d0) then
                  nact(ng)=nact(ng)+1
                  iact(nact(ng),ng)=ns1
                  if (rss.gt.1.0d0) then
                     nout_flag=1
                     tau(ns1,ng)=rss*tau(ns1,ng)
                     tau_update(ns1,ng)=rss*tau_update(ns1,ng)
                     ng_update(ng)=1
                  endif
               endif
            enddo
            if (nout_flag.eq.1) nout=nout+1
         enddo
       else
         do ng=1+ngrph(iph-1),ngrph(iph)
            nout_flag=0
            nact(ng)=0
            do ns1=1,nsys(iph)
                call Calc_J2(ng,J2,s)
                rss=sqrt(J2)/tau(ns1,ng)
                if (rss.ge.0.98) then
                    nact(ng)=nact(ng)+1
                    iact(nact(ng),ng)=ns1
                endif
            enddo
            if (nout_flag.eq.1) nout=nout+1
         enddo
       endif
      enddo
      if (nout.gt.nout_old) then
         nout_old=nout
         write(12,*)
         write(12,*) 'WARNING'
         write(12,*) 'THERE WERE ',nout,' GRAINS OUT OF THE SCYS'
      endif
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE g_average
c **********************************************************************
c *** Calculates the averages and deviations for the stress rate,the ***
c *** strain rate, the stress, the strain and the pressure.          ***
c **********************************************************************
c *** VERSION: 24/APR/97
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Array dimensions:                                              ***
      DIMENSION strav(6),strdev(6),etrav(6),etrdev(6)
      DIMENSION stav(6),stdev(6),etav(6),etdev(6)
c ______________________________________________________________________
c
c *** Read and write formats                                         ***
    1 FORMAT(1h ,6d12.4)
    2 FORMAT(1h ,2(1x,6d11.3,1x,6f7.4))
    3 FORMAT(1h ,6f12.4)
c ______________________________________________________________________
c
      presss =(stss(1)+stss(2)+stss(3))/3.d0
      presav =0.d0
      presdev=0.d0
      do ng=1,ngrain
         prescs =(stcs(1,ng)+stcs(2,ng)+stcs(3,ng))/3.d0
         presav =presav +prescs   *wgt(ng)
         presdev=presdev+prescs**2*wgt(ng)
      enddo
      presdev=dsqrt(dabs(presdev-presav**2))
c
      do i=1,6
         strav(i)=0.d0
         strdev(i)=0.d0
         etrav(i)=0.d0
         etrdev(i)=0.d0
         stav(i)=0.d0
         stdev(i)=0.d0
         etav(i)=0.d0
         etdev(i)=0.d0
         do ng=1,ngrain
            strav(i)=strav(i)+strcs(i,ng)*wgt(ng)
            strdev(i)=strdev(i)+strcs(i,ng)**2*wgt(ng)
            etrav(i)=etrav(i)+etrcs(i,ng)*wgt(ng)
            etrdev(i)=etrdev(i)+etrcs(i,ng)**2*wgt(ng)
            stav(i)=stav(i)+stcs(i,ng)*wgt(ng)
            stdev(i)=stdev(i)+stcs(i,ng)**2*wgt(ng)
            etav(i)=etav(i)+etcs(i,ng)*wgt(ng)
            etdev(i)=etdev(i)+etcs(i,ng)**2*wgt(ng)
         enddo
      enddo
c
      strnorm=0.d0
      etrnorm=0.d0
      stnorm =0.d0
      etnorm =0.d0
      do i=1,6
         strnorm=strnorm+strav(i)**2 * profac(i)
         etrnorm=etrnorm+etrav(i)**2 * profac(i)
         stnorm =stnorm +stav(i)**2  * profac(i)
         etnorm =etnorm +etav(i)**2  * profac(i)
      enddo
      presdev=presdev/sqrt(stnorm)
      do i=1,6
         strdev(i)=dsqrt(dabs(strdev(i)-strav(i)**2))/dsqrt(strnorm)
         etrdev(i)=dsqrt(dabs(etrdev(i)-etrav(i)**2))/dsqrt(etrnorm)
         stdev(i) =dsqrt(dabs(stdev(i)-stav(i)**2))  /dsqrt(stnorm)
         etdev(i) =dsqrt(dabs(etdev(i)-etav(i)**2))  /dsqrt(etnorm)
      enddo
c     
      write(11,*)
      write(11,*) 'Bound. Cond., Av. and Dev. STRESS RATE (normalized)'
      write(11,1) strss
      write(11,1) strav
      write(11,3) strdev
      write(11,*) 'Bound. Cond., Av. and Dev. STRAIN RATE (normalized)'
      write(11,1) etrss
      write(11,1) etrav
      write(11,3) etrdev
      write(11,*)
      write(11,*) 'Bound. Cond., Av. and Dev. STRESS (normalized)'
      write(11,1) stss
      write(11,1) stav
      write(11,3) stdev
      write(11,*) 'Bound. Cond., Av. and Dev. STRAIN (normalized)'
      write(11,1) etss
      write(11,1) etav
      write(11,3) etdev
      write(11,*) 'Bound. pressure, Av. Press. and Dev. (normalized)'
      write(11,1) presss,presav,presdev
c
      write(15,2) etrss,etrdev,etss,etdev
      write(16,2) strss,strdev,stss,stdev
c ______________________________________________________________________
c
      do iph=1,nph
         do i=1,6
            etelssph(i,iph)=0.d0
            etssph(i,iph)=0.d0
            stssph(i,iph)=0.d0
            do ng=1+ngrph(iph-1),ngrph(iph)
               do j=1,6
                  etelssph(i,iph)=etelssph(i,iph)+scs2(i,j,ng)*
     #                 stcs(j,ng)*wgt(ng)*profac(j)
               enddo
               etssph(i,iph)=etssph(i,iph)+etcs(i,ng)*wgt(ng)
               stssph(i,iph)=stssph(i,iph)+stcs(i,ng)*wgt(ng)
            enddo
            etelssph(i,iph) = etelssph(i,iph)/wph(iph)
            etssph(i,iph) = etssph(i,iph)/wph(iph)
            stssph(i,iph) = stssph(i,iph)/wph(iph)
         enddo
      enddo
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE g_modulus
c **********************************************************************
c *** Calculates the single crystal tensor of the incremental consti-***
c *** tutive law for all the grains for each subset of active loading***
c *** systems. Checks the positiveness of the shear rates and the ac-***
c *** tive loading condition.                                        ***
c **********************************************************************
c *** USES:    g_verify    lubksb    ludcmp                          ***
c **********************************************************************
c *** VERSION: 12/OCT/94                                             ***
c **********************************************************************
c *** Parameter definitions:                                         ***
      PARAMETER (TOLER_DET=1.d-20)
c ______________________________________________________________________
c
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Array dimensions:                                              ***
      REAL J2
      DIMENSION aux21(6,6),x(NSLS,NSLS),y(NSLS,NSLS),indx(NSLS)
      DIMENSION s(6)
c ______________________________________________________________________
c
c *** Starts the calculation                                         ***
      do iph=1,nph
         do ng=1+ngrph(iph-1),ngrph(iph)
            igverify=0
            if (nact(ng).eq.0) then
               do i=1,6
                  do j=1,6
                     acs2(i,j,ng)=ccs2(i,j,ng)
                  enddo
               enddo
               igverify=1
               call g_state(ng)
            else
               do while (igverify.eq.0.and.nact(ng).ne.0)
                  do ns1=1,nact(ng)
                     n1=iact(ns1,ng)
                     voce=thet1(n1,iph)
                     if(tau1(n1,iph).gt.1.d-3*tau0(n1,iph)) then
                        thet0x=thet0(n1,iph)
                        thet1x=thet1(n1,iph)
                        fact  =gamtot(ng)*thet0x/tau1(n1,iph)
                        voce  =voce+(thet0x-thet1x+thet1x*fact)*
     #                       exp(-fact)
                     endif
c
                     do ns2=1,nact(ng)
                        n2=iact(ns2,ng)
                        x(ns1,ns2)= voce * h(n1,n2,iph)
                        do i=1,6
                           do j=1,6
                              x(ns1,ns2)=x(ns1,ns2)+mcs(i,n1,ng)*
     #                             mcs(j,n2,ng)*ccs2(i,j,ng)*
     #                             profac(i)*profac(j)
                           enddo
                        enddo
                     enddo
                  enddo
                if(iVM(iph).eq.0) then
                  call ludcmp(x,nact(ng),NSLS,indx,d)
                  do ns1=1,nact(ng)
                     d=d*x(ns1,ns1)
                  enddo
                  if (dabs(d).lt.TOLER_DET) then
                     nact(ng)=nact(ng)-1
                     igverify=0
c     write(*,*) ng,' Look for other combination DET=0'
                  else
                     do ns1=1,nact(ng)
                        do ns2=1,nact(ng)
                           y(ns1,ns2)=(ns1/ns2)*(ns2/ns1)
                        enddo
                     enddo
                     do ns1=1,nact(ng)
                        call lubksb(x,nact(ng),NSLS,indx,y(1,ns1))
                     enddo
                     do ns1=1,nact(ng)
                        do j=1,6
                           f(j,ns1,ng)=0.d0
                           do ns2=1,nact(ng)
                              n2=iact(ns2,ng)
                              do i=1,6
                                 f(j,ns1,ng)=f(j,ns1,ng)+y(ns1,ns2)*
     #                                ccs2(i,j,ng)
     #                                *mcs(i,n2,ng)*profac(i)
                              enddo
                           enddo
                        enddo
                     enddo
                     do i=1,6
                        do j=1,6
                           aux21(i,j)=id2(i,j)
                           do ns1=1,nact(ng)
                              n1=iact(ns1,ng)
                              aux21(i,j)=aux21(i,j)-mcs(i,n1,ng)*
     #                             f(j,ns1,ng)
                           enddo
                        enddo
                     enddo
                     do i=1,6
                        do j=1,6
                           acs2(i,j,ng)=0.d0
                           do k=1,6
                              acs2(i,j,ng)=acs2(i,j,ng)+ccs2(i,k,ng)*
     #                             aux21(k,j)*profac(k)
                           enddo
                        enddo
                     enddo
c
c *** Enforces the symmetry of the calc. moduli                      ***
c             do i=1,6
c               do j=i+1,6
c                 acs2(i,j,ng)=0.5d0*(acs2(i,j,ng)+acs2(j,i,ng))
c                 acs2(j,i,ng)=acs2(i,j,ng)
c               enddo
c             enddo
c
                     call g_state(ng)
                     call g_verify(ng,igverify)
                  endif
                else
                  call calc_J2(ng,J2,s)
                  call Calc_Lc_VM(ng,J2,s,voce)
                  call g_state(ng)
                  call g_verify(ng,igverify)
                endif
               enddo
               if (nact(ng).eq.0) then
c           write(*,*) ng,' !!! WARNING: Achieve zero system state'
                  do i=1,6
                     do j=1,6
                        acs2(i,j,ng)=ccs2(i,j,ng)
                     enddo
                  enddo
                  igverify=1
                  call g_state(ng)
               endif
            endif
         enddo
      enddo
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE g_state(ng)
c **********************************************************************
c *** Evaluates the stress and strain rate state in ecah grain       ***
c **********************************************************************
c *** USES:    invten                                                ***
c **********************************************************************
c *** VERSION: 12/OCT/94                                             ***
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Array dimensions:                                              ***
      DIMENSION aux11(6),aux21(6,6),aux22(6,6)
c ______________________________________________________________________
c
      do i=1,6
        do j=1,6
          aux21(i,j)=aef(i,j)+acs2(i,j,ng)
        enddo
      enddo
      call invten(aux21,aux22)
      do i=1,6
        aux11(i)=0.d0
        do j=1,6
          aux11(i)=aux11(i)+acs2(i,j,ng)*alfacs(j,ng)*deltemp*profac(j)
        enddo
      enddo
      do i=1,6
        etrcs(i,ng)=0.d0
        do j=1,6
          etrcs(i,ng)=etrcs(i,ng)+aux22(i,j)*profac(j)
     #                *(auxsample(j)+aux11(j))
        enddo
      enddo
      do i=1,6
        strcs(i,ng)=0.d0
        do j=1,6
          strcs(i,ng)=strcs(i,ng)+acs2(i,j,ng)*(etrcs(j,ng)
     #                -alfacs(j,ng)*deltemp)*profac(j)
        enddo
      enddo
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE g_verify(ng,igverify)
c **********************************************************************
c *** Tests if the condition of active-loading is fulfilled for the  ***
c *** tentative set in routine G_MODULUS. If it is verified (igverify***
c *** =1), if not then (igverify=0) and reduce the NACT number.      ***
c **********************************************************************
c *** USES:    g_state                                               ***
c **********************************************************************
c *** VERSION: 13/FEB/98                                             ***
c **********************************************************************
c *** Parameter constants:                                           ***
      PARAMETER (ERROR_LOAD=1.d-3) !Error of the active loading condit.
c ______________________________________________________________________
c
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
      DIMENSION aux6(6)
      REAL J2,s(6)
c ______________________________________________________________________
c
c *** Starts the calculation                                         ***
      do i=1,nph
         if (ng.gt.ngrph(i-1)) iph=i
      enddo
      igverify=1
      if(iVM(iph).eq.0) then
      if (nact(ng).ne.0) then
        do ns1=1,nsys(iph)
          gamd(ns1,ng)=0.d0
        enddo
        do ns1=1,nact(ng)
          n1=iact(ns1,ng)
          do i=1,6
            gamd(n1,ng)=gamd(n1,ng)+f(i,ns1,ng)*(etrcs(i,ng)
     #                  -alfacs(i,ng)*deltemp)*profac(i)
          enddo
        enddo
        ns1=1
        do while(ns1.le.nact(ng))
          n1=iact(ns1,ng)
          if (gamd(n1,ng).lt.0.d0) then
c            write(*,*) ng,' Look for other combination GAMMA<0'
c            write(12,*) ng,' Look for other combination GAMMA<0'
c            write(12,*) 'in system',n1
            igverify=0
            nact(ng)=nact(ng)-1
            do ns2=ns1,nact(ng)
              iact(ns2,ng)=iact(ns2+1,ng)
            enddo
            ns1=nact(ng)
          endif
          ns1=ns1+1
        enddo
        if (igverify.ne.0) then
          neload=0
          do ns1=1,nsys(iph)

            voce=thet1(ns1,iph)
            if(tau1(ns1,iph).gt.1.d-3*tau0(n1,iph)) then
              thet0x=thet0(ns1,iph)
              thet1x=thet1(ns1,iph)
              fact  =gamtot(ng)*thet0x/tau1(ns1,iph)
              voce  =voce+(thet0x-thet1x+thet1x*fact)*exp(-fact)
            endif

            taud(ns1,ng)=0.d0
            do ns2=1,nact(ng)
              n2=iact(ns2,ng)
              taud(ns1,ng)=taud(ns1,ng)+voce*h(ns1,n2,iph)*gamd(n2,ng)
            enddo
          enddo
          do ns1=1,nact(ng)
            n1=iact(ns1,ng)
            rssd=0.d0
            do i=1,6
              rssd=rssd+mcs(i,n1,ng)*strcs(i,ng)*profac(i)
            enddo
            control_load=dabs((rssd-taud(n1,ng))/taud(n1,ng))
            if (control_load.gt.ERROR_LOAD) then
              neload=neload+1
c             write(12,*)
c             write(12,*) 'NG: ',ng,'       RSSD>TAUD in SYSTEM: ',n1
c             write(*,*) 'NG: ',ng,'       RSSD>TAUD in SYSTEM: ',n1
c             write(*,*)
            endif
          enddo
          if (neload.ne.0) then
            write(*,*) ng,' Look for other combination RSSD>TAUD'
            nact(ng)=nact(ng)-1
            igverify=0
          endif
        endif
      endif
      else
        do i=1,6
          aux6(i)=etrcs(i,ng)
          do j=1,6
              aux6(i)=aux6(i)-scs2(i,j,ng)*strcs(j,ng)*profac(j)
          enddo
        enddo
        aequiv=0.0d0
        do i=1,6
            aequiv=aequiv+aux6(i)*aux6(i)*profac(i)
        enddo
        aequiv=sqrt(aequiv/1.5)
c       Assigning the "slip rate" to be the equivalent plastic strain
        do ns1=1,nsys(iph)
            gamd(ns1,ng)=0.0
        enddo
        do ns1=1,nact(ng)
            n1=iact(ns1,ng)
            gamd(n1,ng)=aequiv;
        enddo
        do ns1=1,nsys(iph)
            voce=thet1(ns1,iph)
            if(tau1(ns1,iph).gt.1.d-3*tau0(n1,iph)) then
                thet0x=thet0(ns1,iph)
                thet1x=thet1(ns1,iph)
                fact  =gamtot(ng)*thet0x/tau1(ns1,iph)
                voce  =voce+(thet0x-thet1x+thet1x*fact)*exp(-fact)
            endif
            taud(ns1,ng)=0.d0
            do ns2=1,nact(ng)
                n2=iact(ns2,ng)
                taud(ns1,ng)=taud(ns1,ng)+voce*h(ns1,n2,iph)*gamd(n2,ng)
            enddo
        enddo
c       Checking the loading condition (eq 20.28, p.322)
        call Calc_J2(ng,J2,s)
        rssd=0.0
        do i=1,6
          rssd=rssd+s(i)*strcs(i,ng)*profac(i)
        enddo
        rssd=rssd/(2.0*sqrt(J2))
        control_load=abs(rssd-taud(n1,ng))
        if (control_load.gt.ERROR_LOAD) then
            write(*,*) ng,' The von Mises phase is not loading'
            pause
            nact(ng)=nact(ng)-1
            igverify=0
        else
            igverify=1
        endif
      endif
c ______________________________________________________________________
c
      return
      END
C
C *****************************************************************************
C
      SUBROUTINE histogram(v,ncomp,norient,wrtunit)
c **********************************************************************
c *** Makes a histogram for each component of the vector 'v'.
c *** The value of each component is weighted by the volume fraction
c *** of the associated orientation, and accumulated in each interval
c *** of the histogram.
c *** Writes the histogram into unit 'wrtunit'
c **********************************************************************
c *** VERSION: 19/04/95                                              ***
c **********************************************************************
c *** VARIABLES:
c *** ncomp: number of components in 'v' to be averaged.
c *** norient: number of orientations
c *** v(0,1:norient): volume fraction of each orientation.
c *** v(1:ncomp,1:norient): value of each component for each orient.
c **********************************************************************
c
      PARAMETER (NINT=10)
      IMPLICIT REAL*8 (a-h,o-z)
      DIMENSION v(0:ncomp,norient)
      INTEGER wrtunit
c
    1 FORMAT(/1h,'COMPONENT:',i2,5x,'MIN=',d12.4,5x,
     #      'MAX=',d12.4,5x,'AVER=',d12.4)
    2 FORMAT(/1h,'# grs  % abs.wgt.  % rel.wgt.',
     #          '         X_bot         X_mid         X_top')
    3 FORMAT(1h ,i4 ,2f12.5 ,3d14.4)
c
      wgt_tot=0.d0
      do nv=1,norient
        wgt_tot=wgt_tot+v(0,nv)
      enddo
c
      do i=1,ncomp
        v_max=v(i,1)
        v_min=v(i,1)
        v_ave=0.d0
        do nv=2,norient
          if (v(i,nv).gt.v_max) v_max=v(i,nv)
          if (v(i,nv).lt.v_min) v_min=v(i,nv)
          v_ave=v_ave+v(i,nv)*v(0,nv)
        enddo
        v_ave=v_ave/wgt_tot
        write(wrtunit,1) i,v_min,v_max,v_ave
        write(wrtunit,2)
c
        if (v_max .gt. 0.d0) v_max=v_max*1.001d0
        if (v_max .le. 0.d0) v_max=v_max*0.999d0
        if (v_min .gt. 0.d0) v_min=v_min*0.999d0
        if (v_min .le. 0.d0) v_min=v_min*1.001d0
        v_int=(v_max-v_min)/NINT
c
        do ni=1,NINT
          nvalues_int=0
          wgt_int=0.d0
          bot_int=v_min+(ni-1)*v_int
          top_int=v_min+ ni   *v_int
          cen_int=(bot_int+top_int)/2.d0
          do nv=1,norient
            if (v(i,nv).gt.bot_int .and. v(i,nv).le.top_int) then
              nvalues_int=nvalues_int+1
              wgt_int=wgt_int+v(0,nv)
            endif
          enddo
          wgt_abs=wgt_int        *100.d0
          wgt_rel=wgt_int/wgt_tot*100.d0
          write(wrtunit,3) nvalues_int,wgt_abs,wgt_rel,
     #                     bot_int,cen_int,top_int
        enddo
        write(wrtunit,*)
      enddo
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE INVTEN(A,AI)
c **********************************************************************
C *** CALCULATES THE INVERSE AI OF THE TENSOR A USING THE 6X6 VOIGT  ***
C *** REPRESENTATION.                                                ***
c **********************************************************************
c *** USES:    LUDCMP    LUBKSB    SVDCMP                            ***
c **********************************************************************
c *** VERSION: 12/OCT/94                                             ***
c **********************************************************************
      IMPLICIT REAL*8(A-H,O-Z)
      DIMENSION A(6,6),AI(6,6),AX(6,6)
      DIMENSION ID(6,6),INDX(6)
      DIMENSION U(6,6),V(6,6),W(6)
      REAL*8 INVFAC,ID2,ID
      COMMON/VOIG/IJV(6,2),INVFAC(6,6),PROFAC(6),ID2(6,6)
C
      ANORM=0.D0
      DO 5 I=1,6
      DO 5 J=1,6
      ANORM=ANORM+(A(I,J)*A(I,J))*PROFAC(I)*PROFAC(J)
    5 AX(I,J)=A(I,J)
      ANORM=DSQRT(ANORM)
      DO 6 I=1,6
      DO 6 J=1,6
    6 AX(I,J)=AX(I,J)/ANORM
C
      CALL LUDCMP(AX,6,6,INDX,DET)
      DO I=1,6
        DET=DET*AX(I,I)
      ENDDO
      IF (DABS(DET).GE.1.D-80) THEN
        DO I=1,6
          DO J=1,6
            ID(I,J)=0.d0
          ENDDO
          ID(I,I)=1.d0
        ENDDO
        DO I=1,6
          CALL LUBKSB(AX,6,6,INDX,ID(1,I))
        ENDDO
        DO I=1,6
          DO J=1,6
            AI(I,J)=ID(I,J)*INVFAC(I,J)/ANORM
          ENDDO
        ENDDO
      ELSE
       PRINT *, 'SINGULAR MATRIX IN INVTEN. DET = ',DET
       PRINT *, 'WILL MAKE SINGULAR VALUE DECOMPOSITION AND CORRECT'
       WRITE(11,*)
       WRITE(11,'(1H ,78(''-''))')
       WRITE(11,*) 'SINGULAR MATRIX IN INVTEN. DET = ',DET
       WRITE(11,*) 'Matrix:'
       WRITE(11,'(6F13.6)') A
        DO 10 I=1,6
        DO 10 J=1,6
   10   U(I,J)=A(I,J)/ANORM
       WRITE(11,*) 'Normalized matrix:'
       WRITE(11,'(6F13.6)') U
        CALL SVDCMP(U,6,6,6,6,W,V)
c       WRITE(11,*) 'EIGENVALUES OF THE MATRIX (SHOULD BE NON NEGATIVE)'
c       WRITE(11,'(6D13.6)') W
        WMAX=0.D0
        DO 12 I=1,6
        IF(W(I).GT.WMAX) WMAX=W(I)
   12   CONTINUE
        WMIN=WMAX*1.D-5
        DO 14 I=1,6
        IF(W(I).LT.WMIN) W(I)=WMIN
   14   CONTINUE
c       WRITE(11,*) 'CORRECTED EIGENVALUES OF THE MATRIX'
c       WRITE(11,'(6D13.6)') W
C *** CORRECTS THE MATRIX TO MAKE IT NON SINGULAR.
        DO 15 I=1,6
        DO 15 J=1,6
        A(I,J)=0.D0
        DO 15 K=1,6
   15   A(I,J)=A(I,J)+U(I,K)*W(K)*V(J,K)
        DO I=1,6
          DO J=1,6
            A(I,J)=A(I,J)*ANORM
          ENDDO
        ENDDO
c       WRITE(11,*) 'CORRECTED MATRIX'
c       WRITE(11,'(6F13.6)') A
c       WRITE(11,'(1H ,78(''-''))')
c       WRITE(11,*)
C
C *** CALCULATES THE INVERSE USING THE SVD RELATIONS.
        DO 16 I=1,6
        DO 16 J=1,6
        AI(I,J)=0.D0
        DO 16 K=1,6
   16   AI(I,J)=AI(I,J)+V(I,K)*(1.D0/W(K))*U(J,K)
        DO I=1,6
          DO J=1,6
            AI(I,J)=AI(I,J)/ANORM
          ENDDO
        ENDDO
C
        DO 20 I=1,6
        DO 20 J=1,6
   20   AI(I,J)=AI(I,J)*INVFAC(I,J)
      ENDIF
      RETURN
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE LUBKSB(A,N,NP,INDX,B)
      IMPLICIT REAL*8 (A-H,O-Z)
      DIMENSION A(NP,NP),INDX(N),B(N)
      II=0
      DO 12 I=1,N
        LL=INDX(I)
        SUM=B(LL)
        B(LL)=B(I)
        IF (II.NE.0)THEN
          DO 11 J=II,I-1
            SUM=SUM-A(I,J)*B(J)
11        CONTINUE
        ELSE IF (SUM.NE.0.D0) THEN
          II=I
        ENDIF
        B(I)=SUM
12    CONTINUE
      DO 14 I=N,1,-1
        SUM=B(I)
        IF(I.LT.N)THEN
          DO 13 J=I+1,N
            SUM=SUM-A(I,J)*B(J)
13        CONTINUE
        ENDIF
        B(I)=SUM/A(I,I)
14    CONTINUE
      RETURN
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE LUDCMP(A,N,NP,INDX,D)
      PARAMETER (NMAX=2500,TINY=1.0D-20)
      IMPLICIT REAL*8 (A-H,O-Z)
      DIMENSION A(NP,NP),INDX(N),VV(NMAX)
      D=1.D0
      DO 12 I=1,N
        AAMAX=0.
        DO 11 J=1,N
          IF (DABS(A(I,J)).GT.AAMAX) AAMAX=DABS(A(I,J))
11      CONTINUE
        IF (AAMAX.EQ.0.D0) PAUSE 'Singular matrix.'
        VV(I)=1.D0/AAMAX
12    CONTINUE
      DO 19 J=1,N
        IF (J.GT.1) THEN
          DO 14 I=1,J-1
            SUM=A(I,J)
            IF (I.GT.1)THEN
              DO 13 K=1,I-1
                SUM=SUM-A(I,K)*A(K,J)
13            CONTINUE
              A(I,J)=SUM
            ENDIF
14        CONTINUE
        ENDIF
        AAMAX=0.D0
        DO 16 I=J,N
          SUM=A(I,J)
          IF (J.GT.1)THEN
            DO 15 K=1,J-1
              SUM=SUM-A(I,K)*A(K,J)
15          CONTINUE
            A(I,J)=SUM
          ENDIF
          DUM=VV(I)*DABS(SUM)
          IF (DUM.GE.AAMAX) THEN
            IMAX=I
            AAMAX=DUM
          ENDIF
16      CONTINUE
        IF (J.NE.IMAX)THEN
          DO 17 K=1,N
            DUM=A(IMAX,K)
            A(IMAX,K)=A(J,K)
            A(J,K)=DUM
17        CONTINUE
          D=-D
          VV(IMAX)=VV(J)
        ENDIF
        INDX(J)=IMAX
        IF(J.NE.N)THEN
          IF(A(J,J).EQ.0.D0) A(J,J)=TINY
          DUM=1.D0/A(J,J)
          DO 18 I=J+1,N
            A(I,J)=A(I,J)*DUM
18        CONTINUE
        ENDIF
19    CONTINUE
      IF(A(N,N).EQ.0.D0) A(N,N)=TINY
      RETURN
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE plasticity (step,temp,i_control_var)
c **********************************************************************
c *** Evaluates the plastic activity in each step of the process     ***
c *** Average active systems, shears, twinning volume fractions      ***
c *** Relative activity of each plastic mechanism                    ***
c **********************************************************************
c *** VERSION 12/OCT/94                                              ***
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
      DIMENSION shear_tot(NPHX),vfrac_tot(NPHX)
c ______________________________________________________________________
c
c *** Read and write formats:                                        ***
    1 FORMAT(1h ,'STATISTIC OF SLIP ACTIVITY:')
    2 FORMAT(1h ,'Average number of load_active systems:',2x,f8.4)
    3 FORMAT(1h ,'No plastic activity')
    4 FORMAT(1h ,'Fraction of total shear:')
    5 FORMAT(1h ,'Mode #:',i3,2x,'Activity:',1x,f8.4,1x,'%')
    6 Format(1h ,'Twinning volume fraction:')
    7 FORMAT(1h ,'There is not twinning activation.')
    8 FORMAT(1h ,'Twin mode:',i3,2x,'Volume fraction:',1x,f8.4)
    9 FORMAT(1h ,'Total number of grains that plastify:',i6)
   10 FORMAT(1h , f10.5,3x,5f7.3)
c ______________________________________________________________________
c
c *** Starts the calculation:                                        ***
      write(12,*)
      ngtotact=0
      actav=0.d0
      do iph=1,nph
         do mo=1,nmodes(iph)
            shear_mod(mo,iph)=0.d0
            vfrac_mod(mo,iph)=0.d0
         enddo
      enddo
      do iph=1,nph
         do ng=1+ngrph(iph-1),ngrph(iph)
            if (nact(ng).ne.0) then
               ngtotact=ngtotact+1
               actav=actav+nact(ng)*wgt(ng)
               nst=0
               do mo=1,nmodes(iph)
                  do isys=1,nsm(mo,iph)
                     nst=nst+1
                     shear_mod(mo,iph) = shear_mod(mo,iph)
     #                    +gamd(nst,ng)*wgt(ng)
                     shear_mod_acum(mo,iph) = shear_mod_acum(mo,iph)
     #                    +gamd(nst,ng)*wgt(ng)
                     if (itw(mo,iph).eq.1) then
                        vfrac_mod(mo,iph) = vfrac_mod(mo,iph)
     #                       +gamd(nst,ng)/stw(mo,iph)*step*wgt(ng)
                        vfrac_mod_acum(mo,iph) = vfrac_mod_acum(mo,iph)
     #                       +gamd(nst,ng)/stw(mo,iph)*step*wgt(ng)
                     endif
                  enddo
               enddo
            endif
         enddo
      enddo
      do iph=1,nph
         shear_tot(iph)=0.d0
         vfrac_tot(iph)=0.d0
         do mo=1,nmodes(iph)
            shear_tot(iph)=shear_tot(iph)+shear_mod(mo,iph)
            vfrac_tot(iph)=vfrac_tot(iph)+vfrac_mod(mo,iph)
         enddo
      enddo
c
c *** Write the results in "EPSC?.OUT"
      if (i_control_var.eq.0) xref=temp
      if (i_control_var.ge.1) xref=etss(i_control_var)
      if (i_control_var.ge.4) xref=stss(i_control_var-3)
c
      write(12,1)
      write(12,2) actav
      do iph=1,nph
         if (shear_tot(iph).eq.0.d0) then
            write(12,3)
            write(17,10) xref,(shear_mod(mo,iph),mo=1,nmodes(iph)),actav
         else
            write(12,4)
            do mo=1,nmodes(iph)
               write(12,5) mo,shear_mod(mo,iph)/shear_tot(iph)*100.d0
            enddo
            write(17,10) xref,(shear_mod(mo,iph)/shear_tot(iph)
     #           ,mo=1,nmodes(iph)),actav
         endif
         write(12,6)
         if (vfrac_tot(iph).eq.0.d0) then
            write(12,7)
         else
            do mo=1,nmodes(iph)
               if (itw(mo,iph).eq.1) then
                  write(12,8) mo,vfrac_mod(mo,iph)
               endif
            enddo
         endif
      enddo
      write(12,*)
      write(12,9) ngtotact
      if (ngtotact.ne.0) then
        do ng=1,ngrain
          if (nact(ng).ne.0) then
            if (ngtotact.le.ngrprn.or.ng.le.ngrprn) then
              write(12,*)
              write(12,*) 'NG:',ng,' NACT:',nact(ng)
              write(12,'(1h ,''IACT:'')')
              write(12,*) (iact(ns1,ng),ns1=1,nact(ng))
            endif
          endif
        enddo
      endif
c
c *** Calculates accum. plastic shear for each set of diffracting grains.
c *** Does an average per grain instead of a weighted average. The idea is
c *** to make the result independent of the volume fraction of grains
c *** contained in each diffracting set.
c
      do iph=1,nph
         if (ndiff(iph).gt.0) then
            do nd=1,ndiff(iph)
               dummy=0.d0
               do ng=1,ngrset(nd,iph)
                  ngset=igrset(nd,ng,iph)
                  nst=0
                  do mo=1,nmodes(iph)
                     do isys=1,nsm(mo,iph)
                        nst=nst+1
                        dummy=dummy+dabs(gamd(nst,ngset))
                     enddo
                  enddo
               enddo
               shear_dif_acum(nd,iph)=shear_dif_acum(nd,iph)
     #              +dummy/ngrset(nd,iph)
            enddo
         endif
      enddo
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE sc(iopt,liter,iflagcond,e2)
c **********************************************************************
c *** Solves the selfconsistent equation for the sample modulus      ***
c **********************************************************************
c *** USES:    eshelby     invten       voigt                        ***
c **********************************************************************
c *** VERSION: 12/OCT/94                                             ***
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Array dimensions:                                              ***
      DIMENSION e2(6,6),e2i(6,6),ass4(3,3,3,3),av2v(6,6),av2r(6,6)
      DIMENSION x1(6),x2(3,3),aux11(6),anew(6,6)
      DIMENSION aux21(6,6),aux22(6,6),aux23(6,6),aux24(6,6)
c ______________________________________________________________________
c
c *** Read and write formats:                                        ***
    1 FORMAT(1h ,'VOIGT AVERAGE FOR THE MODULUS:')
    2 FORMAT(1h ,6d12.4)
    3 FORMAT(1h ,'REUSS AVERAGE FOR THE MODULUS:')
    4 FORMAT(1h ,'For iteration = ',i3,' the error is ',d12.4)
    5 FORMAT(1h+,'ITER: ',i3,'   ERROR: ',d12.4)
    6 FORMAT(1h ,'THE CONVERGENCE IS NOT ACHIEVED AFTER ',i3,
     #         ' ITERACIONS',/,
     #1h ,'ABNORMAL PROGRAM STOP......................')
c ______________________________________________________________________
c
c *** Sets the flags, counters and assign the auxiliar variables.    ***
      iguess=1
c ______________________________________________________________________
c
c *** Calc. the VOIGT and REUSS averages                             ***
      if (iopt.ne.1) then
         do i=1,6
            do j=1,6
               av2v(i,j)=0.d0
               aux23(i,j)=0.d0
            enddo
         enddo
         do ng=1,ngrain
c          if(ng.eq.143) write(11,2) ass2
            do i=1,6
               do j=1,6
                  aux21(i,j)=acs2(i,j,ng)
               enddo
            enddo
            call invten(aux21,aux22)
            do i=1,6
               do j=1,6
                  av2v(i,j)=av2v(i,j)+acs2(i,j,ng)*wgt(ng)
                  aux23(i,j)=aux23(i,j)+aux22(i,j)*wgt(ng)
               enddo
            enddo
         enddo
         call invten(aux23,av2r)
c       write(11,*)
c       write(11,1)
c       write(11,2) av2v
c       write(11,*)
c       write(11,3)
c       write(11,2) av2r
      endif
c ______________________________________________________________________
c
c *** Sets the iteration number.                                     ***
      if (iopt.eq.0) then
         niter=itmax_mod
      else
         niter=1
      endif
c ______________________________________________________________________
c
c *** Does the LOOP for the iterative procedure                      ***
c
      do while (iguess.le.niter)
c
c         write(*,*) 'SELFCONSISTENT MODULI:'
c         write(*,2) ass2
c         read(*,*)
c
c *** Calc. ESHELBY tensor asociated with stiffnes and ellip. axis   ***
         call voigt(x1,x2,ass2,ass4,3)
ccc        call eshelby(ass4,ass2,e2,axis)
ccc        call eshelby3x3(ass4,ass2,e2,axis,4,1)
         call eshelby3x3new(ass4,ass2,e2,axis,4,1)
c
c *** Calc. the effective stiffnes:aef = ass2 * ( e2**(-1) - I )     ***
         call invten(e2,e2i)
         do i=1,6
            do j=1,6
               aef(i,j)=0.d0
               do k=1,6
                  aef(i,j)=aef(i,j)
     #                 +ass2(i,k)*(e2i(k,j)-id2(k,j))*profac(k)
               enddo
            enddo
         enddo
c
c *** Activate DO loop to reduce AEF and force a more compliant interaction.
cc      do i=1,6
cc        do j=1,6
cc          aef(i,j)=0.5d0*aef(i,j)
cc        enddo
cc      enddo
c
         if (iopt.ne.1) then
c
c *** Calc. the tensor                                               ***
c *** anew = < acs2 * (acs2+aef)**(-1) > * (ass2+aef)                ***
c *** anew = < acs2 *    aux21         > * (ass2+aef)                ***
c *** anew =          aux22              * (ass2+aef)                ***
c
            do i=1,6
               aux11(i)=0.d0
               do j=1,6
                  aux22(i,j)=0.d0
                  aux23(i,j)=0.d0
               enddo
            enddo
c     
            do ng=1,ngrain
               do i=1,6
                  do j=1,6
                     aux24(i,j)=acs2(i,j,ng)+aef(i,j)
                  enddo
               enddo
               call invten(aux24,aux21)
               do i=1,6
                  do j=1,6
                     aux23(i,j)=aux23(i,j)+aux21(i,j)*wgt(ng)
                     do k=1,6
                        aux22(i,j)=aux22(i,j)+acs2(i,k,ng)
     #                       *aux21(k,j)*profac(k)*wgt(ng)
                        aux11(i)=aux11(i)+aux21(i,j)*acs2(j,k,ng)
     #                       *alfacs(k,ng)*profac(j)*profac(k)*wgt(ng)
                     enddo
                  enddo
               enddo
            enddo
c
            do i=1,6
               do j=1,6
                  anew(i,j)=0.d0
                  do k=1,6
                     anew(i,j)=anew(i,j)+aux22(i,k)*(ass2(k,j)
     #                    +aef(k,j))*profac(k)
                  enddo
               enddo
            enddo
c
c *** Enforces the symmetry of the calc. moduli                      ***
            do i=1,6
               do j=i+1,6
                  anew(i,j)=0.5d0*(anew(i,j)+anew(j,i))
                  anew(j,i)=anew(i,j)
               enddo
            enddo
c
c *** Checks for the convergence of (anew-ass2) to zero              ***
            error=0.d0
            anorm=0.d0
            do i=1,6
               do j=1,6
                  anorm=anorm+(ass2(i,j)+anew(i,j))*(ass2(i,j)
     #                 +anew(i,j))*profac(i)*profac(j)
                  error=error+(ass2(i,j)-anew(i,j))*(ass2(i,j)-
     #                 anew(i,j))*profac(i)*profac(j)
                  ass2(i,j)=anew(i,j)
               enddo
            enddo
            error=dsqrt(error)/(0.5*dsqrt(anorm))
c     
            if (iopt.eq.0) then
               write(11,4) iguess,error
               write(*,4) iguess,error
            else
               write(11,4) liter,error
               write(*,4) liter,error
            endif
c      	   write(*,*) 'SELFCONSISTENT MODULI from epscNp:'
c   	      write(*,2) ass2
c	         read(*,*)
            if (error.le.error_mod) then
               iguess=itmax_mod+1
               iflagcond=0
            else
               if (iguess.eq.itmax_mod) then
                  write(11,*)
                  write(11,6) itmax_mod
                  write(*,*)
                  write(*,6) itmax_mod
                  read(*,*)
                  stop
               endif
               iguess=iguess+1
               iflagcond=1
            endif
c
         else
            iguess=iguess+1
         endif
c
c *** Closes the DO WHILE for the iterations                         ***
      enddo
c
      if (iopt.ne.1) then
c
c *** Evaluates the independent term for the sample                  ***
         call invten(aux23,aux24)
         call invten(anew,aux22)
         do i=1,6
            alfass(i)=0.d0
            do j=1,6
               do k=1,6
                  alfass(i)=alfass(i)+aux22(i,j)*aux24(j,k)*aux11(k)
     #                 *profac(j)*profac(k)
               enddo
            enddo
         enddo
c ______________________________________________________________________
c
         if (iflagcond.eq.0) then
c          write(11,*)
c          write(11,1)
c          write(11,2) av2v
c          write(11,*)
c          write(11,3)
c          write(11,2) av2r
c          write(11,*)
c          write(11,*) 'SELFCONSISTENT MODULI:'
c          write(11,2) ass2
c          write(11,*) 'THERMAL COEFFICIENTS:'
c          write(11,2) alfass
         endif
      endif
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE s_state
c **********************************************************************
c *** Evaluates the stress and strain rate in sample                 ***
c **********************************************************************
c *** USES:    ludcmp      lubksb                                    ***
c **********************************************************************
c *** VERSION: 12/OCT/94                                             ***
c **********************************************************************
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
c *** Array dimensions:                                              ***
      DIMENSION aux11(6),aux21(6,6),indx(6)
c ______________________________________________________________________
c
      do i=1,6
         aux11(i)=-1.d0*istbc(i)*strbc(i)
         do j=1,6
            aux11(i)=aux11(i)+ass2(i,j)*(ietbc(j)*etrbc(j)
     #           -alfass(j)*deltemp)*profac(j)
            aux21(i,j)=ietbc(j)*(i/j)*(j/i)-
     #           istbc(j)*ass2(i,j)*profac(j)
         enddo
      enddo
c
      call ludcmp(aux21,6,6,indx,d)
      call lubksb(aux21,6,6,indx,aux11)
      do i=1,6
         etrss(i)=ietbc(i)*etrbc(i)+istbc(i)*aux11(i)
         strss(i)=istbc(i)*strbc(i)+ietbc(i)*aux11(i)
      enddo
c
c     write(11,*)
c     write(11,*) 'Polycrystal Stress Rate State:'
c     write(11,'(1h ,6d12.4)') strss
c     write(11,*) 'Polycrystal Strain Rate State:'
c     write(11,'(1h ,6d12.4)') etrss
c
c *** Calculate the auxiliar vector to use in G_STATE.               ***
      do i=1,6
         aux11(i)=0.d0
         auxsample(i)=0.d0
         do j=1,6
            aux11(i)=aux11(i)+(aef(i,j)+ass2(i,j))*etrss(j)*profac(j)
            auxsample(i)=auxsample(i)+ass2(i,j)*alfass(j)*deltemp
     #           *profac(j)
         enddo
         auxsample(i)=aux11(i)-auxsample(i)
      enddo
c______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE SVDCMP(A,M,N,MP,NP,W,V)
      PARAMETER (NMAX=2500)
      IMPLICIT REAL*8 (A-H,O-Z)
      DIMENSION A(MP,NP),W(NP),V(NP,NP),RV1(NMAX)
      PRINT *, 'SCDCMP called!!!'
      G=0.D0
      SCALE=0.D0
      ANORM=0.D0
      DO 25 I=1,N
        L=I+1
        RV1(I)=SCALE*G
        G=0.D0
        S=0.D0
        SCALE=0.D0
        IF (I.LE.M) THEN
          DO 11 K=I,M
            SCALE=SCALE+DABS(A(K,I))
11        CONTINUE
          IF (SCALE.NE.0.D0) THEN
            DO 12 K=I,M
              A(K,I)=A(K,I)/SCALE
              S=S+A(K,I)*A(K,I)
12          CONTINUE
            F=A(I,I)
            G=-DSIGN(DSQRT(S),F)
            H=F*G-S
            A(I,I)=F-G
            IF (I.NE.N) THEN
              DO 15 J=L,N
                S=0.D0
                DO 13 K=I,M
                  S=S+A(K,I)*A(K,J)
13              CONTINUE
                F=S/H
                DO 14 K=I,M
                  A(K,J)=A(K,J)+F*A(K,I)
14              CONTINUE
15            CONTINUE
            ENDIF
            DO 16 K= I,M
              A(K,I)=SCALE*A(K,I)
16          CONTINUE
          ENDIF
        ENDIF
        W(I)=SCALE *G
        G=0.D0
        S=0.D0
        SCALE=0.D0
        IF ((I.LE.M).AND.(I.NE.N)) THEN
          DO 17 K=L,N
            SCALE=SCALE+DABS(A(I,K))
17        CONTINUE
          IF (SCALE.NE.0.D0) THEN
            DO 18 K=L,N
              A(I,K)=A(I,K)/SCALE
              S=S+A(I,K)*A(I,K)
18          CONTINUE
            F=A(I,L)
            G=-DSIGN(DSQRT(S),F)
            H=F*G-S
            A(I,L)=F-G
            DO 19 K=L,N
              RV1(K)=A(I,K)/H
19          CONTINUE
            IF (I.NE.M) THEN
              DO 23 J=L,M
                S=0.D0
                DO 21 K=L,N
                  S=S+A(J,K)*A(I,K)
21              CONTINUE
                DO 22 K=L,N
                  A(J,K)=A(J,K)+S*RV1(K)
22              CONTINUE
23            CONTINUE
            ENDIF
            DO 24 K=L,N
              A(I,K)=SCALE*A(I,K)
24          CONTINUE
          ENDIF
        ENDIF
        ANORM=DMAX1(ANORM,(DABS(W(I))+DABS(RV1(I))))
25    CONTINUE
      DO 32 I=N,1,-1
        IF (I.LT.N) THEN
          IF (G.NE.0.D0) THEN
            DO 26 J=L,N
              V(J,I)=(A(I,J)/A(I,L))/G
26          CONTINUE
            DO 29 J=L,N
              S=0.D0
              DO 27 K=L,N
                S=S+A(I,K)*V(K,J)
27            CONTINUE
              DO 28 K=L,N
                V(K,J)=V(K,J)+S*V(K,I)
28            CONTINUE
29          CONTINUE
          ENDIF
          DO 31 J=L,N
            V(I,J)=0.D0
            V(J,I)=0.D0
31        CONTINUE
        ENDIF
        V(I,I)=1.D0
        G=RV1(I)
        L=I
32    CONTINUE
      DO 39 I=N,1,-1
        L=I+1
        G=W(I)
        IF (I.LT.N) THEN
          DO 33 J=L,N
            A(I,J)=0.D0
33        CONTINUE
        ENDIF
        IF (G.NE.0.D0) THEN
          G=1.D0/G
          IF (I.NE.N) THEN
            DO 36 J=L,N
              S=0.D0
              DO 34 K=L,M
                S=S+A(K,I)*A(K,J)
34            CONTINUE
              F=(S/A(I,I))*G
              DO 35 K=I,M
                A(K,J)=A(K,J)+F*A(K,I)
35            CONTINUE
36          CONTINUE
          ENDIF
          DO 37 J=I,M
            A(J,I)=A(J,I)*G
37        CONTINUE
        ELSE
          DO 38 J= I,M
            A(J,I)=0.D0
38        CONTINUE
        ENDIF
        A(I,I)=A(I,I)+1.D0
39    CONTINUE
      DO 49 K=N,1,-1
        DO 48 ITS=1,30
          DO 41 L=K,1,-1
            NM=L-1
c
cnt --> modified 09/04/98 to avoid warning
c
            tiny=DABS(RV1(L))/ANORM
            if(tiny.le.1.d-6) go to 2
            tiny=DABS(W(NM))/ANORM
            if(tiny.le.1.d-6) go to 1

c            IF ((DABS(RV1(L))+ANORM).EQ.ANORM)  GO TO 2
c            IF ((DABS(W(NM)) +ANORM).EQ.ANORM)  GO TO 1
cnt --> end of modification

41        CONTINUE
1         C=0.D0
          S=1.D0
          DO 43 I=L,K
            F=S*RV1(I)

cnt --> modified 09/04/98 to avoid warning
            tiny=DABS(F)/ANORM
            if(tiny.le.1.d-6) then

c            IF ((DABS(F)+ANORM).NE.ANORM) THEN
cnt --> end
              G=W(I)
              H=DSQRT(F*F+G*G)
              W(I)=H
              H=1.D0/H
              C= (G*H)
              S=-(F*H)
              DO 42 J=1,M
                Y=A(J,NM)
                Z=A(J,I)
                A(J,NM)=(Y*C)+(Z*S)
                A(J,I)=-(Y*S)+(Z*C)
42            CONTINUE
            ENDIF
43        CONTINUE
2         Z=W(K)
          IF (L.EQ.K) THEN
            IF (Z.LT.0.D0) THEN
              W(K)=-Z
              DO 44 J=1,N
                V(J,K)=-V(J,K)
44            CONTINUE
            ENDIF
            GO TO 3
          ENDIF
          IF (ITS.EQ.30) PAUSE 'No convergence in 30 iterations'
          X=W(L)
          NM=K-1
          Y=W(NM)
          G=RV1(NM)
          H=RV1(K)
          F=((Y-Z)*(Y+Z)+(G-H)*(G+H))/(2.D0*H*Y)
          G=DSQRT(F*F+1.D0)
          F=((X-Z)*(X+Z)+H*((Y/(F+DSIGN(G,F)))-H))/X
          C=1.D0
          S=1.D0
          DO 47 J=L,NM
            I=J+1
            G=RV1(I)
            Y=W(I)
            H=S*G
            G=C*G
            Z=DSQRT(F*F+H*H)
            RV1(J)=Z
            C=F/Z
            S=H/Z
            F= (X*C)+(G*S)
            G=-(X*S)+(G*C)
            H=Y*S
            Y=Y*C
            DO 45 NM=1,N
              X=V(NM,J)
              Z=V(NM,I)
              V(NM,J)= (X*C)+(Z*S)
              V(NM,I)=-(X*S)+(Z*C)
45          CONTINUE
            Z=DSQRT(F*F+H*H)
            W(J)=Z
            IF (Z.NE.0.D0) THEN
              Z=1.D0/Z
              C=F*Z
              S=H*Z
            ENDIF
            F= (C*G)+(S*Y)
            X=-(S*G)+(C*Y)
            DO 46 NM=1,M
              Y=A(NM,J)
              Z=A(NM,I)
              A(NM,J)= (Y*C)+(Z*S)
              A(NM,I)=-(Y*S)+(Z*C)
46          CONTINUE
47        CONTINUE
          RV1(L)=0.D0
          RV1(K)=F
          W(K)=X
48      CONTINUE
3       CONTINUE
49    CONTINUE
      RETURN
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE VOIGT(T1,T2,C2,C4,IOPT)
C **********************************************************************
C *** TRANSFORMS 6X6 MATRIX C2 INTO FOURTH ORDER TENSOR C4 IF IOPT=1 ***
C *** AND VICEVERSA IF IOPT=2.                                       ***
C *** TRANSFORMS 6X1 MATRIX T1 INTO SECOND ORDER TENSOR T2 IF IOPT=3 ***
C *** AND VICEVERSA IF IOPT=4.                                       ***
c **********************************************************************
c *** VERSION 12/OCT/94                                              ***
c **********************************************************************
      IMPLICIT REAL*8 (A-H,O-Z)
      DIMENSION T1(6),T2(3,3),C2(6,6),C4(3,3,3,3)
      REAL*8 INVFAC,ID2
      COMMON/VOIG/IJV(6,2),INVFAC(6,6),PROFAC(6),ID2(6,6)
C
      IF(IOPT.EQ.1) THEN
         DO I=1,6
            I1=IJV(I,1)
            I2=IJV(I,2)
            T2(I1,I2)=T1(I)
            T2(I2,I1)=T1(I)
         ENDDO
      ENDIF
C
      IF(IOPT.EQ.2) THEN
         DO I=1,6
            I1=IJV(I,1)
            I2=IJV(I,2)
            T1(I)=T2(I1,I2)
         ENDDO
      ENDIF
C
      IF(IOPT.EQ.3) THEN
         DO I=1,6
            I1=IJV(I,1)
            I2=IJV(I,2)
            DO J=1,6
               J1=IJV(J,1)
               J2=IJV(J,2)
               C4(I1,I2,J1,J2)=C2(I,J)
               C4(I2,I1,J1,J2)=C2(I,J)
               C4(I1,I2,J2,J1)=C2(I,J)
               C4(I2,I1,J2,J1)=C2(I,J)
            ENDDO
         ENDDO
      ENDIF
C
      IF(IOPT.EQ.4) THEN
         DO I=1,6
            I1=IJV(I,1)
            I2=IJV(I,2)
            DO J=1,6
               J1=IJV(J,1)
               J2=IJV(J,2)
               C2(I,J)=C4(I1,I2,J1,J2)
            ENDDO
         ENDDO
      ENDIF
C
      RETURN
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE zirconium(temp)
c **********************************************************************
c *** Calculates stiffness moduli in units of GPa as a function of   ***
c *** temperature                                                    ***
c **********************************************************************
c *** USES:    invten                                                ***
c **********************************************************************
c *** VERSION 12/OCT/94                                              ***
c **********************************************************************
c *** Sets units of stiffness:                                       ***
      PARAMETER (C_REF=1.d+3)
c ______________________________________________________________________
c
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
c ______________________________________________________________________
c
      tempf=temp+deltemp
c ______________________________________________________________________
c
c *** These coefficients are for ZIRCONIUM                           ***
c *** Fits the curves obtained by:                                   ***
c *** FISHER,E.S. and RENKEN,C.J. Phys.Rev. 135 2A (1964) A482-A494. ***
      ccc2(1,1)=(159430-58.133*tempf+1.447d-2*tempf**2
     #     -4.099d-6*tempf**3)/C_REF
      ccc2(2,2)=ccc2(1,1)
      ccc2(1,2)=(61357+49.009*tempf-4.1198d-2*tempf**2
     #     +1.396d-5*tempf**3)/C_REF
      ccc2(2,1)=ccc2(1,2)
      ccc2(1,3)=(64912+1.8131d-2*tempf+4.4831d-3*tempf**2
     #     -3.704d-6*tempf**3)/C_REF
      ccc2(2,3)=ccc2(1,3)
      ccc2(3,1)=ccc2(1,3)
      ccc2(3,2)=ccc2(1,3)
      ccc2(3,3)=(174080-30.996*tempf-1.3754d-3*tempf**2
     #     -6.997d-9*tempf**3)/C_REF
      ccc2(4,4)=(37290-20.79*tempf+1.1433d-2*tempf**2
     #     -5.0173d-6*tempf**3)/C_REF
      ccc2(5,5)=ccc2(4,4)
      ccc2(6,6)=(ccc2(1,1)-ccc2(1,2))/2
c
      call invten(ccc2,scc2)
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      SUBROUTINE zinc(temp,iph)
c **********************************************************************
c *** Calculates stiffness moduli in units of GPa as a function of   ***
c *** temperature                                                    ***
c **********************************************************************
c *** USES:    invten                                                ***
c **********************************************************************
c *** VERSION 01/MAY/2000                                            ***
c **********************************************************************
c *** Sets units of stiffness (the reference is in MPa and the       ***
c *** program uses GPa:                                              ***
      PARAMETER (C_REF=1.d+3)
c ______________________________________________________________________
c
c *** Includes the file with parameter, dimensions and common        ***
      INCLUDE 'epscnp.dim'
      DIMENSION dummy1(6,6),dummy2(6,6)
c ______________________________________________________________________
c
      tempf=temp+deltemp
c ______________________________________________________________________
c
c *** These coefficients are for ZINC                                ***
c *** This subroutine should only be used within the temperature     ***
c *** interval given in the reference ( XX to XX K)                  ***
      DO i=1,6
         DO j=1,6
            ccc2ph(i,j,iph) =0.d0
         END DO
      END DO
      ccc2ph(1,1,iph)=(159430-58.133*tempf+1.447d-2*tempf**2
     #     -4.099d-6*tempf**3)/C_REF
      ccc2ph(2,2,iph)=ccc2ph(1,1,iph)
      ccc2ph(1,2,iph)=(61357+49.009*tempf-4.1198d-2*tempf**2
     #     +1.396d-5*tempf**3)/C_REF
      ccc2ph(2,1,iph)=ccc2ph(1,2,iph)
      ccc2ph(1,3,iph)=(64912+1.8131d-2*tempf+4.4831d-3*tempf**2
     #     -3.704d-6*tempf**3)/C_REF
      ccc2ph(2,3,iph)=ccc2ph(1,3,iph)
      ccc2ph(3,1,iph)=ccc2ph(1,3,iph)
      ccc2ph(3,2,iph)=ccc2ph(1,3,iph)
      ccc2ph(3,3,iph)=(174080-30.996*tempf-1.3754d-3*tempf**2
     #     -6.997d-9*tempf**3)/C_REF
      ccc2ph(4,4,iph)=(37290-20.79*tempf+1.1433d-2*tempf**2
     #     -5.0173d-6*tempf**3)/C_REF
      ccc2ph(5,5,iph)=ccc2ph(4,4,iph)
      ccc2ph(6,6,iph)=(ccc2ph(1,1,iph)-ccc2ph(1,2,iph))/2
c
      DO i=1,6
         DO j=1,6
            dummy1(i,j) = ccc2ph(i,j,iph)
         END DO
      END DO
      call invten(dummy1,dummy2)
      DO i=1,6
         DO j=1,6
            scc2ph(i,j,iph) = dummy2(i,j)
         END DO
      END DO
c
      DO i=1,6
         alfaccph(i,iph) =0.d0
      END DO
      alfaccph(1,iph) = 1.0 + 1.0*tempf + 1.0*tempf**2
      alfaccph(2,iph) = 1.0 + 1.0*tempf + 1.0*tempf**2
      alfaccph(3,iph) = 1.0 + 1.0*tempf + 1.0*tempf**2
c ______________________________________________________________________
c
      return
      END
c
c ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C
C ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C
C     SUBROUTINE ESHELBY3x3   ---->   VERSION 06/08/97
C
C     CALCULATES THE ESHELBY TENSOR ASSOCIATED WITH AN ELLIPSOIDAL
C     INCLUSION HAVING AXIS(I) AS MAIN AXES AND EMBEDDED IN A FULLY
C     ANISOTROPIC MEDIUM WITH STIFNESSESS COEFFICIENTS C4(I,J,K,L)
C     REFERRED TO THE ELLIPSOID AXES.
C     MAKES EXPLICIT USE OF ORTHOTROPIC SYMMETRY (ISYM=4 OR LOWER)
C
C     THE INTEGRATION IS PERFORMED USING A GAUSSIAN QUADRATURE SCHEME.
C     THE ROUTINE "GAULEG" IS CALLED WHEN IOP=0, TO
C     CALCULATE THE GAUSS INTEGRATION POINTS AND THE WEIGHTS.
C
C     THIS ROUTINE IS A MODIFICATION OF ESHELBY4x4 USED IN SELFPOL6.
C
C ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C
      SUBROUTINE ESHELBY3x3(C4,C2,ESH2,AXIS,ISYM,IOP)
C
      PARAMETER (NGAUSS=10)
      IMPLICIT REAL*8 (A-H,O-Z)
C
      DIMENSION C4(3,3,3,3),C2(6,6),ESH2(6,6)
      DIMENSION AXIS(3),AXISX(3),X(3),A2(6,6)
      DIMENSION XP(2*NGAUSS),WP(2*NGAUSS)
      DIMENSION CXX(3,3),CXXX(3,3)
      COMMON/voig    /ijv(6,2),invfac(6,6),profac(6),id2(6,6)
      PI=3.1415926535898
C
      IF (IOP.EQ.0) THEN
C
C *** WHEN IOP=0 IT CALCULATES THE POINTS AND THE WEIGHTS ASSOCIATED WITH
C *** THE GAUSSIAN QUADRATURE METHOD.
C
        FACTOR=1.D0/(8.D0*PI)
        XL=0.D0
        XH=PI
        NPOINTS=2*NGAUSS
        LOOPLIM=6
        IF (ISYM.LE.4) THEN
          FACTOR=4.D0*FACTOR
          XH=XH/2.D0
          NPOINTS=NPOINTS/2
          LOOPLIM=LOOPLIM/2
        ENDIF
        CALL GAULEG(XL,XH,XP,WP,NPOINTS)
C
      ELSE
C
C *** INTEGRATES THE GREEN'S TENSOR OVER HALF OF THE ELLIPSOID FOR THE
C *** LESS SYMMETRIC CASES (isym>4)
C *** INTEGRATES ONLY THE NON-ZERO TERMS OVER A QUADRANT WHEN THE MEDIUM
C *** HAS ORTHOTROPIC (isym=4) OR MORE THAN ORTHOTROPIC SYMMETRY (isym<4).
C
        AXISMIN=DMIN1(AXIS(1),AXIS(2),AXIS(3))
        DO I=1,3
          AXISX(I)=AXIS(I)/AXISMIN
        ENDDO
        DO 10 I=1,6
          DO 10 J=1,6
   10       A2(I,J)=0.D0
C
        DO 60 M=1,NPOINTS
          CPH=DCOS(XP(M))
          SPH=DSIN(XP(M))
          DO 50 N=1,NPOINTS
            CTH=DCOS(XP(N))
            STH=DSIN(XP(N))
            X(1)=STH*CPH/AXISX(1)
            X(2)=STH*SPH/AXISX(2)
            X(3)=    CTH/AXISX(3)
C
            DO 30 I=1,3
              DO 30 K=1,3
                CXXX(I,K)=0.D0
                DO 30 J=1,3
                  DO 30 L=1,3
   30               CXXX(I,K)=CXXX(I,K)+C4(I,J,K,L)*X(J)*X(L)
C
            CALL INVSYM3X3(CXXX,CXX)
C
            DO 40 I=1,LOOPLIM
              I1=IJV(I,1)
              I2=IJV(I,2)
              DO 40 J=I,LOOPLIM
                J1=IJV(J,1)
                J2=IJV(J,2)
                G= CXX(I1,J1)*X(I2)*X(J2)+CXX(I2,J1)*X(I1)*X(J2) +
     #             CXX(I1,J2)*X(I2)*X(J1)+CXX(I2,J2)*X(I1)*X(J1)
   40           A2(I,J)=A2(I,J)+STH*G*WP(N)*WP(M)
            IF (LOOPLIM.EQ.3) THEN
              DO 45 I=4,6
                I1=IJV(I,1)
                I2=IJV(I,2)
                G= CXX(I1,I1)*X(I2)*X(I2)+CXX(I2,I1)*X(I1)*X(I2) +
     #             CXX(I1,I2)*X(I2)*X(I1)+CXX(I2,I2)*X(I1)*X(I1)
   45           A2(I,I)=A2(I,I)+STH*G*WP(N)*WP(M)
            ENDIF
C
   50     CONTINUE
   60   CONTINUE
C
        DO I=1,6
          DO J=I,6
            A2(I,J)=FACTOR*A2(I,J)
            A2(J,I)=A2(I,J)
          ENDDO
        ENDDO
C
C *** CALCULATES ESHELBY TENSOR AS A PRODUCT OF TWO 6X6 MATRICES.
        DO 90 I=1,6
          DO 90 J=1,6
            ESH2(I,J)=A2(I,1)*C2(1,J)+A2(I,2)*C2(2,J) +
     #                A2(I,3)*C2(3,J)+2.D0*(A2(I,4)*C2(4,J) +
     #                A2(I,5)*C2(5,J)+A2(I,6)*C2(6,J))
   90   CONTINUE
C
      ENDIF
      RETURN
      END




C
C ***********************************************************************
C     SUBROUTINE ESHELBY3X3NEW      --->      version 26/JULY/99
C     B. Clausen
C
C     CALCULATES ESHELBY TENSOR.
C     ALGORITHMS ARE BASED IN Lebensohn et al, MSMSE 6 (1998) p.447.
C ***********************************************************************

      SUBROUTINE ESHELBY3X3NEW(C4,C2,ESH2,AXIS,ISYM,IOP)
c
      IMPLICIT REAL*8 (A-H,O-Z)
c
      PARAMETER (NGAUSS=20)
C
      DIMENSION C4(3,3,3,3),C2(6,6),AXIS(3),X1(6),A1(6)
      DIMENSION AA1X(6),AA2X(3,3),AAWW1X(6),AAWW2X(3,3)
c      
      DIMENSION XP(NGAUSS),WP(NGAUSS),SINF(NGAUSS),COSF(NGAUSS)
      DIMENSION GAMMA2(6,6),ESH2(6,6),GAMMA4(3,3,3,3),ESH4(3,3,3,3)
      DIMENSION AAWW1(6,NGAUSS**2),AA1(6,NGAUSS**2),ALPHA(3,NGAUSS**2)
      COMMON/voig    /ijv(6,2),invfac(6,6),profac(6),id2(6,6)
C     ***********************************************************************
C     INITIALIZATION RUN
C     Calculates Gauss-Legendre integration points and weights in the
c     interval [0,pi].
C     Initializes arrays associated with each point to avoid repeating
C     its calculation at every call.
C     ***********************************************************************
c      
      IF(IOP.EQ.0) THEN
         PI=4.D0*DATAN(1.D0)
         FACTOR=1.0/(2.0*PI)
c
         XL=0.D0
         XH=PI
         NPOINTS=NGAUSS
         LOOPLIM=6
         IF (ISYM.LE.4) THEN
            FACTOR=4.D0*FACTOR
            XH=XH/2.D0
            NPOINTS=NPOINTS/2
            LOOPLIM=LOOPLIM/2
         ENDIF
         CALL GAULEG(XL,XH,XP,WP,NPOINTS)
         DO N=1,NPOINTS
            SINF(N)=DSIN(XP(N))
            COSF(N)=DCOS(XP(N))
         ENDDO
         DO ITHETA=1,NPOINTS
            SINT=SINF(ITHETA)
            COST=COSF(ITHETA)
            SIMBTET=FACTOR*WP(ITHETA)*SINT
            DO IPHI=1,NPOINTS
               NY=IPHI+(ITHETA-1)*NPOINTS
               WW=SIMBTET*WP(IPHI)
               ALPHA(1,NY)=SINT*COSF(IPHI)
               ALPHA(2,NY)=SINT*SINF(IPHI)
               ALPHA(3,NY)=COST
               DO I=1,3
                  DO J=1,3
                     AA2X(I,J)  =ALPHA(I,NY)*ALPHA(J,NY)
                     AAWW2X(I,J)=AA2X(I,J)*WW
                  ENDDO
               ENDDO
c         
c     Transform second order tensors aaww2x & aa2x into Voigt vectors.
c
               CALL VOIGT(AA1X  ,AA2X  ,DUM,DUM,2)
               CALL VOIGT(AAWW1X,AAWW2X,DUM,DUM,2)
               DO I=1,6
                  AA1(I,NY)  =AA1X(I)
                  AAWW1(I,NY)=AAWW1X(I)
               ENDDO
            ENDDO
         ENDDO
         RETURN
      ENDIF
c      
C ***********************************************************************
C     CALCULATION OF ESHELBY TENSORS
C     For given stiffness C4 and ellipsoid axes AXIS
C ***********************************************************************
      IF(IOP.EQ.1) THEN
         DO I=1,6
            DO J=1,6
               GAMMA2(I,J)=0.D0
            ENDDO
         ENDDO
c     
         ABC=AXIS(1)*AXIS(2)*AXIS(3)
         DO NY=1,NPOINTS**2     ! Double integration
c     
            DO I=1,6
               AA1X(I)=AA1(I,NY)
            ENDDO
c
            CALL ESH_MULT(C2,AA1X,A1)
            CALL ESH_INV(A1,X1)
c
            RO3=((ALPHA(1,NY)*AXIS(1))**2+(ALPHA(2,NY)*AXIS(2))**2+
     #           (ALPHA(3,NY)*AXIS(3))**2)**1.5
            ABCORO3=ABC/RO3
c
            DO I=1,LOOPLIM
               DO J=1,LOOPLIM
                  GAMMA2(I,J)=GAMMA2(I,J)+AAWW1(I,NY)*X1(J)*ABCORO3
               ENDDO
            ENDDO
            IF (LOOPLIM.EQ.3) THEN
               DO I=4,6
                  GAMMA2(I,I)=GAMMA2(I,I) + 
     #                 AAWW1(I,NY)*X1(I)*ABCORO3
               ENDDO
            ENDIF
         ENDDO                  ! end of loop over double integration
c     
c     ***************************************************************
c         
c     ** Go back to the 3*3*3*3 notation
         CALL VOIGT(DUM,DUM,GAMMA2,GAMMA4,3)
c
c   Compute symmetric (distortion) Eshelby tensor from Eq.B9.
c       ESH4(n,m,k,l)=0.5*(gamma4(m,j,n,i)+gamma4(n,j,m,i))*c4(i,j,k,l)
c
         DO L=1,3
            DO K=1,3
               DO M=1,3
                  DO N=1,3
                     ESH4(N,M,K,L) = 0.D0
                     DO J=1,3
                        DO I=1,3
                           ESH4(N,M,K,L) =ESH4(N,M,K,L) + 
     #   0.5*(GAMMA4(M,J,N,I)+GAMMA4(N,J,M,I))*C4(I,J,K,L)
                        ENDDO
                     ENDDO
                  ENDDO
               ENDDO
            ENDDO
         ENDDO
c     
         CALL VOIGT(DUM,DUM,ESH2,ESH4,4)
c         write(*,'('' eshelby3x3new'')')
c         write(*,'(6f12.6)') ((esh2(i,j),j=1,6),i=1,6)
c         read(*,*)
c
      ENDIF                     !  endif for OPTION=1
c     
      RETURN
      END
C
C
C ***********************************************************
C
C ***********************************************************
      SUBROUTINE ESH_MULT(B,C,A)
C
C     Performs the multiplication:
C     A(i,k)=B(i,j,k,l)*C(j,l) using Voigt's notation
C     B is a 3*3*3*3 tensor in 6*6 symmetric matrix form
C     C is a 3*3 symmetric tensor in 1x6 vector form
C     A will be a 3*3 symmetric tensor in 1x6 vector form
C     11->1, 22->2, 33->3, 23=32->4, 31=13->5, 12=21->6
C
      IMPLICIT REAL*8 (a-h,o-z)
C
      DIMENSION B(6,6),C(6),A(6)
C
      A(1)=B(1,1)*C(1)+B(6,6)*C(2)+B(5,5)*C(3)
     #     +2*(B(5,6)*C(4)+B(1,5)*C(5)+B(1,6)*C(6))
C     
      A(2)=B(6,6)*C(1)+B(2,2)*C(2)+B(4,4)*C(3)
     #     +2*(B(2,4)*C(4)+B(4,6)*C(5)+B(2,6)*C(6))
C     
      A(3)=B(5,5)*C(1)+B(4,4)*C(2)+B(3,3)*C(3)
     #     +2*(B(3,4)*C(4)+B(3,5)*C(5)+B(4,5)*C(6))
C     
      A(4)=B(5,6)*C(1)+B(2,4)*C(2)+B(3,4)*C(3)
     #     +(B(2,3)+B(4,4))*C(4)
     #     +(B(3,6)+B(4,5))*C(5)
     #     +(B(4,6)+B(2,5))*C(6)
C     
      A(5)=B(1,5)*C(1)+B(4,6)*C(2)+B(3,5)*C(3)
     #     +(B(3,6)+B(4,5))*C(4)
     #     +(B(1,3)+B(5,5))*C(5)
     #     +(B(1,4)+B(5,6))*C(6)
C     
      A(6)=B(1,6)*C(1)+B(2,6)*C(2)+B(4,5)*C(3)
     #     +(B(4,6)+B(2,5))*C(4)
     #     +(B(1,4)+B(5,6))*C(5)
     #     +(B(1,2)+B(6,6))*C(6)
C     
      RETURN
      END
C
C
C ***********************************************************
C
C ***********************************************************
      SUBROUTINE ESH_INV(A,B)
C
C     A is a 3x3 tensor in 1x6 vector representation
C     B will be a 3x3 tensor in 1x6 vector representation
C     11->1, 22->2, 33->3, 23=32->4, 31=13->5, 12=21->6
C
      IMPLICIT REAL*8 (a-h,o-z)
C
      DIMENSION A(6),B(6)
C     
      DET = A(1)*A(2)*A(3) + 2*A(4)*A(5)*A(6) - A(1)*A(4)*A(4)
     #     - A(2)*A(5)*A(5) - A(3)*A(6)*A(6)
C     
      B(1) = ( A(2)*A(3) - A(4)*A(4))/DET
      B(2) = ( A(1)*A(3) - A(5)*A(5))/DET
      B(3) = ( A(1)*A(2) - A(6)*A(6))/DET
      B(4) = (-A(1)*A(4) + A(5)*A(6))/DET
      B(5) = ( A(4)*A(6) - A(2)*A(5))/DET
      B(6) = (-A(3)*A(6) + A(4)*A(5))/DET
C     
      RETURN
      END
C
C ***********************************************************
c
C
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C
C     SUBROUTINE GAULEG(X1,X2,X,W,N)
C
C     Given lower and upper limits of integration (x1 & x2) returns arrays
C     x(n) & w(n) containing abcisas and weights of Gauss-Legendre quadrature
C     formula.
C     Scales interval to (-1,+1) to find the roots. Roots are symmetric with
C     respect to zero. Scales back to the original interval at the end.
C
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
C
      subroutine gauleg(x1,x2,x,w,n)
      implicit real*8(a-h,p-z)
      dimension x(n),w(n)
      parameter(eps=3.d-14)
      pi=4.d0*datan(1.d0)
      m=(n+1)/2
      xm=0.5d0*(x1+x2)
      xl=0.5d0*(x2-x1)
      xn=n
      do 12 i=1,m
      xi=i
      z=dcos(pi*(xi-.25d0)/(xn+0.5d0))
c      write(*,*)'z= ',z,xm
1     continue
      p1=1.d0
      p2=0.d0
      do 11 j=1,n
      xj=j
      p3=p2
      p2=p1
      p1=((2.d0*j-1.d0)*z*p2-(xj-1.d0)*p3)/xj
11    continue
      pp=n*(z*p1-p2)/(z*z-1.d0)
      z1=z
      z=z1-p1/pp
      if(dabs(z-z1).gt.eps) go to 1
      x(i)=xm-xl*z
      x(n+1-i)=xm+xl*z
      w(i)=2.d0*xl/((1.d0-z*z)*pp*pp)
      w(n+1-i)=w(i)
12    continue
      return
      end
C+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
      subroutine invsym3x3 (a,ai)
c
      implicit real*8 (a-h,o-z)
      dimension a(3,3),ai(3,3)
c
      det=a(1,1)*a(2,2)*a(3,3)+2.d0*a(1,2)*a(2,3)*a(1,3)
     #     -a(1,3)*a(2,2)*a(1,3)-a(1,2)*a(1,2)*a(3,3)
     #     -a(2,3)*a(2,3)*a(1,1)
c     
      ai(1,1)=  (a(2,2)*a(3,3)-a(2,3)*a(2,3))/det
      ai(1,2)= -(a(1,2)*a(3,3)-a(1,3)*a(2,3))/det
      ai(1,3)=  (a(1,2)*a(2,3)-a(1,3)*a(2,2))/det
      ai(2,1)=  ai(1,2)
      ai(2,2)=  (a(1,1)*a(3,3)-a(1,3)*a(1,3))/det
      ai(2,3)= -(a(1,1)*a(2,3)-a(1,3)*a(1,2))/det
      ai(3,1)=  ai(1,3)
      ai(3,2)=  ai(2,3)
      ai(3,3)=  (a(1,1)*a(2,2)-a(1,2)*a(1,2))/det
c     
      return
      end
c
c ****************************************************************************
c
      SUBROUTINE TWINNING (ioption,iph)
c *********************************************************************
c     Scans twinning systems in each grain and identifies the one with
c     maximum shear increment.
c     Checks if the latter value exceeds a threshole GAMDTHRES.
c     Associates a transformation strain corresponding to a fixed shear
c     in the twin system with maximum contribution in the grain.
c
c     Keeps track of the volume fraction associated with the original
c     and twinned orientations using an array WGTX. This array is used
c     only inside SUBROUTINE DIF_PLANES.
c     The SC calculation is done using only the starting orientations
c     and weights, without accounting for the twinned fractions
c *********************************************************************
c **** VERSION 24/AUG/98
c *********************************************************************
c
      INCLUDE 'epscnp.dim'
c
      DIMENSION bur(3),aux33(3,3),aux(3,3)
c _____________________________________________________________________
c
c _____________________________________________________________________
c
      if(ioption.eq.0) then
         ngrainx=ngrain
         do ng=1+ngrph(iph-1),ngrph(iph)
            wgtx(ng)=wgt(ng)
            link(ng)=0
            do ns1=1,nsys(iph)
               ktwtag(ns1,ng)=0
            enddo
         enddo
         return
      endif
c     
      ntwgr=0
      deltemp=1.d0
      do iph=1,nph
         do ng=1+ngrph(iph-1),ngrph(iph)
c     
c *** resets to zero the transformation strain
            do i=1,6
               alfacs(i,ng)=0.d0
            enddo
c     
c *** Identifies twinning system with maximum shear. At the same time resets
c *** the CRSS in the twin system that has nucleated in the previous step to
c *** the CRSS for propagation, and tags such system.
            nst=0
            gamdmax=0.d0
            do mo=1,nmodes(iph)
               if(itw(mo,iph).eq.0) nst=nst+nsm(mo,iph)
               if(itw(mo,iph).eq.1) then
                  do isys=1,nsm(mo,iph)
                     nst=nst+1
c     
                     if(gamd(nst,ng).gt.gamdmax) then
                        nstag=nst
                        stwx=stw(mo,iph)
                        gamdmax=gamd(nst,ng)
                     endif
c     
                     if(ktwtag(nst,ng).eq.1) then
                        rss=0.d0
                        do i=1,6
                           rss=rss+mcs(i,nst,ng)*stcs(i,ng)*profac(i)
                        enddo
                        tau(nst,ng)=tauprop
                        if(tau(nst,ng).lt.rss) tau(nst,ng)=rss
                        ktwtag(nst,ng)=2
                     endif
c     
                  enddo
               endif
            enddo
c
c *** For the grains with a tagged twin system checks the threshold condition.
c *** If true, sets back all twinning systems except the active one, and adds
c *** a fixed fraction to the twin related orientation.
c     
            if(gamdmax.ge.gamdthres) then
c     
               do i=1,6
                  alfacs(i,ng)=mcs(i,nstag,ng)*stwx*twvol
               enddo
c     
               ntwgr=ntwgr+1
               write(*,'('' grain #'',i4,'' twins to #'',i4)') 
     #              ng,link(ng)
c     
               if(ktwtag(nstag,ng).eq.2) then
                  wgtx(link(ng))=wgtx(link(ng))+twvol*wgtx(ng)
                  wgtx(ng)      =wgtx(ng)      -twvol*wgtx(ng)
               else if(ktwtag(nstag,ng).eq.0) then
                  ngrainx   =ngrainx+1
                  link(ng)  =ngrainx
                  ktwtag(nstag,ng)=1
                  write(*,'('' grain #'',i4,'' twins to #'',i4)')
     #                 ng,link(ng)
c
c *** Shifts the CRSS in the active twin from nucleation to propagation,
c *** but redefines if the stress is left outside the SCYS.
c *** Deactivates the other twinning systems by rising their CRSS.
                  nst=0
                  do mo=1,nmodes(iph)
                     if(itw(mo,iph).eq.0) nst=nst+nsm(mo,iph)
                     if(itw(mo,iph).eq.1) then
                        do isys=1,nsm(mo,iph)
                           nst=nst+1
                           
cc                if(nst.ne.nstag) then
cc                  tau(nst,ng)=2.d0*tau(nst,ng)
cc                  ktwtag(nst,ng)=-1
cc                endif

                        enddo
                     endif
                  enddo
c     
                  do i=1,3
                     bur(i)=bcs(i,nstag,ng)
                     do j=1,3
                        aux33(i,j)=r(j,i,ng)
                     enddo
                  enddo
                  call twinor(bur,aux33)
                  do i=1,3
                     do j=1,3
                        r(i,j,ngrainx)=aux33(j,i)
                        aux(i,j)      =aux33(j,i)
                     enddo
                  enddo
                  call euler(1,phi(ngrainx),the(ngrainx)
     #                 ,ome(ngrainx),aux)
                  wgtx(link(ng))=wgtx(link(ng))+twvol*wgtx(ng)
                  wgtx(ng)      =wgtx(ng)      -twvol*wgtx(ng)
c     
               else if(ktwtag(nstag,ng).eq.-1) then
                  print *
                  print *, 'A PASSIVE TWIN SYSTEM HAS BEEN TAGGED !!!'
                  read(*,*)
                  stop
               endif
            endif
c     
         enddo
      enddo
c
      if(ngrainx.gt.ngr) then
         write(*,'('' DIMENSION NGR EXCEEDED INSIDE SUBR. TWINNING'')')
         read(*,*)
         stop
      endif
c
      if(ngrainx.gt.ngrain) then
         tottwfr=0.d0
         do ng=ngrain+1,ngrainx
            tottwfr=tottwfr+wgtx(ng)*twvol
         enddo
         write(*,*)
         write(*,'('' TWINNED GRAINS IN THE STEP: '',I5)') ntwgr
         write(*,'('' ACCUMULATED TWIN FRACTION : '',F10.5)') tottwfr
      endif
c
c *** Defines stress in the twinned fraction equal to stress in grain
c *** Calculates elastic moduli of twinned fraction in sample axes.
      do ng=1,ngrain
         ngx=link(ng)
         if(ngx.ne.0) then
            do i=1,6
               stcs(i,ngx)=stcs(i,ng)
            enddo
            call cr_to_sa(ngx,ngx,1)
         endif
      enddo
c     
      return
      end
C
C *****************************************************************************
C     SUBROUTINE TWINOR      --->      VERSION OF 10/AUG/98
C
C     GIVES THE TRANSFORMATION MATRIX 'A' (FROM CRYSTAL TO SAMPLE) OF THE
C     TWINNED RELATED RELATED CRYSTAL.
C     GIVEN THE BURGERS VECTOR OF THE TWIN SYSTEM (IN CRYSTAL AXES) MAKES
C     A ROTATION OF 180 DEG. AROUND IT TO DEFINE THE TWINNED CRYSTAL.
C *****************************************************************************
C
      SUBROUTINE TWINOR(BUR,A)
C
      IMPLICIT REAL*8 (a-h,o-z)
      DIMENSION BUR(3),HPI(3,3),HTW(3,3),A(3,3),AUX(3,3),ATW(3,3)
C
      DATA HPI/-1.,0.,0.,0.,-1.,0.,0.,0.,1./
      PI=4.D0*DATAN(1.D0)
C     
      ANG1=DATAN2(BUR(2),BUR(1))+PI/2.D0
      ANG2=DSQRT(BUR(1)**2+BUR(2)**2)
      ANG2=DATAN2(ANG2,BUR(3))
      CALL EULER (2,ANG1,ANG2,0.D0,AUX)
      
      DO I=1,3
         DO J=1,3
            HTW(I,J)=0.
            DO K1=1,3
               DO K2=1,3
                  HTW(I,J)=HTW(I,J)+AUX(K1,I)*HPI(K1,K2)*AUX(K2,J)
               ENDDO
            ENDDO
         ENDDO
      ENDDO

      DO I=1,3
         DO J=1,3
            ATW(I,J)=0.
            DO K=1,3
               ATW(I,J)=ATW(I,J)+A(I,K)*HTW(K,J)
            ENDDO
         ENDDO
      ENDDO
c
      DO I=1,3
         DO J=1,3
            A(I,J)=ATW(I,J)
         ENDDO
      ENDDO
c
      RETURN
      END
C
C *****************************************************************************
C
      FUNCTION ran2(idum)
      INTEGER idum,IM1,IM2,IMM1,IA1,IA2,IQ1,IQ2,IR1,IR2,NTAB,NDIV
      REAL ran2,AM,EPS,RNMX
      PARAMETER (IM1=2147483563,IM2=2147483399,AM=1./IM1,IMM1=IM1-1,
     #     IA1=40014,IA2=40692,IQ1=53668,IQ2=52774,IR1=12211,IR2=3791,
     #     NTAB=32,NDIV=1+IMM1/NTAB,EPS=1.2e-7,RNMX=1.-EPS)
      INTEGER idum2,j,k,iv(NTAB),iy
      SAVE iv,iy,idum2
      DATA idum2/123456789/, iv/NTAB*0/, iy/0/
      if (idum.le.0) then
         idum=max(-idum,1)
         idum2=idum
         do j=NTAB+8,1,-1
            k=idum/IQ1
            idum=IA1*(idum-k*IQ1)-k*IR1
            if (idum.lt.0) idum=idum+IM1
            if (j.le.NTAB) iv(j)=idum
         enddo
         iy=iv(1)
      endif
      k=idum/IQ1
      idum=IA1*(idum-k*IQ1)-k*IR1
      if (idum.lt.0) idum=idum+IM1
      k=idum2/IQ2
      idum2=IA2*(idum2-k*IQ2)-k*IR2
      if (idum2.lt.0) idum2=idum2+IM2
      j=1+iy/NDIV
      iy=iv(j)-idum2
      iv(j)=idum
      if(iy.lt.1)iy=iy+IMM1
      ran2=min(AM*iy,RNMX)
      return
      END
C
C *****************************************************************************
C
      SUBROUTINE Calc_J2(ng,J2,s)
      INCLUDE 'epscnp.dim'
      REAL J2,p,s(6)
      p=0.0
      do i=1,3
        p=p+stcs(i,ng)
      enddo
      p=p/3.0
      do i=1,3
        s(i)=stcs(i,ng)-p
      enddo
      do i=4,6
        s(i)=stcs(i,ng)
      enddo
      J2=0.0
      do i=1,6
        J2=J2+s(i)*s(i)*profac(i)
      enddo
      J2=J2/2.0
      END
C
C *****************************************************************************
C
      SUBROUTINE Calc_Lc_VM(ng,J2,s,voce)
      INCLUDE 'epscnp.dim'
      REAL J2,s(6),fs(6),voce,dum,aux6(6),aux66(6,6)
      do i=1,6
        fs(i)=s(i)/(2.0*sqrt(J2))
      enddo
      do i=1,6
        aux6(i)=0.d0
        do j=1,6
          aux6(i)=aux6(i)+ccs2(i,j,ng)*fs(j)*profac(j)
        enddo
      enddo
      dum=0.0
      do i=1,6
        dum=dum+aux6(i)*fs(i)*profac(i)
      enddo
      dum=dum+voce/sqrt(3.0)
      do i=1,6
        do j=1,6
          aux66(i,j)=aux6(i)*aux6(j)*profac(i)*profac(j)/dum
        enddo
      enddo
      do i=1,6
        do j=1,6
          acs2(i,j,ng)=ccs2(i,j,ng)-aux66(i,j)
        enddo
      enddo
      END
C
C *****************************************************************************
C
