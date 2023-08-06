*Stress controlling direction 3
*Number of steps in the process:
$Num_Steps                                                                   "nsteps"
*Starting and final temperature:
298. 298.                                                   "temp_s"  "temp_f"
*Enforced temperature dependence of elastic constants (1=YES or 0=NO)?
0                                                                 "i_temp_cij"
*Indexes and values for the stress boundary condition:
       1       1       1       1       1       1                       "istbd"
     0.0   0.0e0   $Stress   0.0e0   0.0e0   0.0e0                      "stbc"
*Indexes and values for the strain boundary condition:
       0       0       0       0       0       0                       "ietbc"
     999     999     999     999     999     999                        "etbc"
*Reset macroscopic strain to zero (1=YES or 0=NO)?
0                                                                     "i_et_0"
*Control process variable: 0=temp , 1,2,3=etss(1,2,3) , 4,5,6=stss(1,2,3)
6                                                              "i_control_var"
*Convergence criterium for the sample moduli:
100  1.e-02                                           "itmax_mod"  "error_mod"
*Maximum number of iterations to select the set of systems in grains:
100                                                              "itmax_grain"
