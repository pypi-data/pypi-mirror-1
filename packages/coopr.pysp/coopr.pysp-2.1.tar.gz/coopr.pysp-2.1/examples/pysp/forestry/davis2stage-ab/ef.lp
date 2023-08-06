\ Begin objective block for master
max 
obj:  1.0 MASTER_EXPECTED_COST_RootNode 
\ End objective block for master

s.t.

\ Begin constraint block for master
MASTER_c_l_ForestDavis8_RootNode_f_(Int1Org5P,Ano1)(None)_:  -1.0 ForestDavis8_f((Int1Org5P,Ano1)) + 1.0 MASTER_RootNode_f((Int1Org5P,Ano1)) >= 0.0

MASTER_c_u_ForestDavis8_RootNode_f_(Int1Org5P,Ano1)(None)_:  -1.0 ForestDavis8_f((Int1Org5P,Ano1)) + 1.0 MASTER_RootNode_f((Int1Org5P,Ano1)) <= 0.0

MASTER_c_l_ForestDavis12_RootNode_gamma_(Org1Org3P,Ano1)(None)_:  -1.0 ForestDavis12_gamma((Org1Org3P,Ano1)) + 1.0 MASTER_RootNode_gamma((Org1Org3P,Ano1)) >= 0.0

MASTER_c_u_ForestDavis12_RootNode_gamma_(Org1Org3P,Ano1)(None)_:  -1.0 ForestDavis12_gamma((Org1Org3P,Ano1)) + 1.0 MASTER_RootNode_gamma((Org1Org3P,Ano1)) <= 0.0

MASTER_c_l_ForestDavis12_RootNode_f_(Int1Org5P,Ano1)(None)_:  -1.0 ForestDavis12_f((Int1Org5P,Ano1)) + 1.0 MASTER_RootNode_f((Int1Org5P,Ano1)) >= 0.0

MASTER_c_u_ForestDavis12_RootNode_f_(Int1Org5P,Ano1)(None)_:  -1.0 ForestDavis12_f((Int1Org5P,Ano1)) + 1.0 MASTER_RootNode_f((Int1Org5P,Ano1)) <= 0.0

MASTER_c_l_ForestDavis16_RootNode_AnoProfit_Ano1(None)_:  -1.0 ForestDavis16_AnoProfit(Ano1) + 1.0 MASTER_RootNode_AnoProfit(Ano1) >= 0.0

MASTER_c_u_ForestDavis16_RootNode_AnoProfit_Ano1(None)_:  -1.0 ForestDavis16_AnoProfit(Ano1) + 1.0 MASTER_RootNode_AnoProfit(Ano1) <= 0.0

MASTER_c_l_ForestDavis4_RootNode_AnoProfit_Ano1(None)_:  -1.0 ForestDavis4_AnoProfit(Ano1) + 1.0 MASTER_RootNode_AnoProfit(Ano1) >= 0.0

MASTER_c_u_ForestDavis4_RootNode_AnoProfit_Ano1(None)_:  -1.0 ForestDavis4_AnoProfit(Ano1) + 1.0 MASTER_RootNode_AnoProfit(Ano1) <= 0.0

MASTER_c_l_ForestDavis4_RootNode_f_(Int1Org5P,Ano1)(None)_:  -1.0 ForestDavis4_f((Int1Org5P,Ano1)) + 1.0 MASTER_RootNode_f((Int1Org5P,Ano1)) >= 0.0

MASTER_c_u_ForestDavis4_RootNode_f_(Int1Org5P,Ano1)(None)_:  -1.0 ForestDavis4_f((Int1Org5P,Ano1)) + 1.0 MASTER_RootNode_f((Int1Org5P,Ano1)) <= 0.0

MASTER_c_l_ForestDavis4_Leaf1_AnoProfit_Ano2(None)_:  -1.0 ForestDavis4_AnoProfit(Ano2) + 1.0 MASTER_Leaf1_AnoProfit(Ano2) >= 0.0

MASTER_c_u_ForestDavis4_Leaf1_AnoProfit_Ano2(None)_:  -1.0 ForestDavis4_AnoProfit(Ano2) + 1.0 MASTER_Leaf1_AnoProfit(Ano2) <= 0.0

MASTER_c_l_ForestDavis16_RootNode_gamma_(Org1Org3P,Ano1)(None)_:  -1.0 ForestDavis16_gamma((Org1Org3P,Ano1)) + 1.0 MASTER_RootNode_gamma((Org1Org3P,Ano1)) >= 0.0

MASTER_c_u_ForestDavis16_RootNode_gamma_(Org1Org3P,Ano1)(None)_:  -1.0 ForestDavis16_gamma((Org1Org3P,Ano1)) + 1.0 MASTER_RootNode_gamma((Org1Org3P,Ano1)) <= 0.0

MASTER_c_l_ForestDavis8_RootNode_delta_(TrackEighteen,Ano1)(None)_:  -1.0 ForestDavis8_delta((TrackEighteen,Ano1)) + 1.0 MASTER_RootNode_delta((TrackEighteen,Ano1)) >= 0.0

MASTER_c_u_ForestDavis8_RootNode_delta_(TrackEighteen,Ano1)(None)_:  -1.0 ForestDavis8_delta((TrackEighteen,Ano1)) + 1.0 MASTER_RootNode_delta((TrackEighteen,Ano1)) <= 0.0

MASTER_c_l_ForestDavis4_RootNode_gamma_(Org1Org3P,Ano1)(None)_:  -1.0 ForestDavis4_gamma((Org1Org3P,Ano1)) + 1.0 MASTER_RootNode_gamma((Org1Org3P,Ano1)) >= 0.0

MASTER_c_u_ForestDavis4_RootNode_gamma_(Org1Org3P,Ano1)(None)_:  -1.0 ForestDavis4_gamma((Org1Org3P,Ano1)) + 1.0 MASTER_RootNode_gamma((Org1Org3P,Ano1)) <= 0.0

MASTER_c_l_ForestDavis16_RootNode_f_(Int1Org5P,Ano1)(None)_:  -1.0 ForestDavis16_f((Int1Org5P,Ano1)) + 1.0 MASTER_RootNode_f((Int1Org5P,Ano1)) >= 0.0

MASTER_c_u_ForestDavis16_RootNode_f_(Int1Org5P,Ano1)(None)_:  -1.0 ForestDavis16_f((Int1Org5P,Ano1)) + 1.0 MASTER_RootNode_f((Int1Org5P,Ano1)) <= 0.0

MASTER_c_l_ForestDavis4_RootNode_delta_(TrackEighteen,Ano1)(None)_:  -1.0 ForestDavis4_delta((TrackEighteen,Ano1)) + 1.0 MASTER_RootNode_delta((TrackEighteen,Ano1)) >= 0.0

MASTER_c_u_ForestDavis4_RootNode_delta_(TrackEighteen,Ano1)(None)_:  -1.0 ForestDavis4_delta((TrackEighteen,Ano1)) + 1.0 MASTER_RootNode_delta((TrackEighteen,Ano1)) <= 0.0

MASTER_c_l_ForestDavis8_RootNode_z_(Exit1,Ano1)(None)_:  -1.0 ForestDavis8_z((Exit1,Ano1)) + 1.0 MASTER_RootNode_z((Exit1,Ano1)) >= 0.0

MASTER_c_u_ForestDavis8_RootNode_z_(Exit1,Ano1)(None)_:  -1.0 ForestDavis8_z((Exit1,Ano1)) + 1.0 MASTER_RootNode_z((Exit1,Ano1)) <= 0.0

MASTER_c_l_ForestDavis12_RootNode_AnoProfit_Ano1(None)_:  -1.0 ForestDavis12_AnoProfit(Ano1) + 1.0 MASTER_RootNode_AnoProfit(Ano1) >= 0.0

MASTER_c_u_ForestDavis12_RootNode_AnoProfit_Ano1(None)_:  -1.0 ForestDavis12_AnoProfit(Ano1) + 1.0 MASTER_RootNode_AnoProfit(Ano1) <= 0.0

MASTER_c_l_ForestDavis12_RootNode_z_(Exit1,Ano1)(None)_:  -1.0 ForestDavis12_z((Exit1,Ano1)) + 1.0 MASTER_RootNode_z((Exit1,Ano1)) >= 0.0

MASTER_c_u_ForestDavis12_RootNode_z_(Exit1,Ano1)(None)_:  -1.0 ForestDavis12_z((Exit1,Ano1)) + 1.0 MASTER_RootNode_z((Exit1,Ano1)) <= 0.0

MASTER_c_l_ForestDavis8_RootNode_gamma_(Org1Org3P,Ano1)(None)_:  -1.0 ForestDavis8_gamma((Org1Org3P,Ano1)) + 1.0 MASTER_RootNode_gamma((Org1Org3P,Ano1)) >= 0.0

MASTER_c_u_ForestDavis8_RootNode_gamma_(Org1Org3P,Ano1)(None)_:  -1.0 ForestDavis8_gamma((Org1Org3P,Ano1)) + 1.0 MASTER_RootNode_gamma((Org1Org3P,Ano1)) <= 0.0

MASTER_c_l_COST_Leaf4_AnoProfit_Ano2(None)_:  1.0 MASTER_EXPECTED_COST_Leaf4 - 1.0 MASTER_Leaf4_AnoProfit(Ano2) >= 0.0

MASTER_c_u_COST_Leaf4_AnoProfit_Ano2(None)_:  1.0 MASTER_EXPECTED_COST_Leaf4 - 1.0 MASTER_Leaf4_AnoProfit(Ano2) <= 0.0

MASTER_c_l_ForestDavis8_Leaf2_AnoProfit_Ano2(None)_:  -1.0 ForestDavis8_AnoProfit(Ano2) + 1.0 MASTER_Leaf2_AnoProfit(Ano2) >= 0.0

MASTER_c_u_ForestDavis8_Leaf2_AnoProfit_Ano2(None)_:  -1.0 ForestDavis8_AnoProfit(Ano2) + 1.0 MASTER_Leaf2_AnoProfit(Ano2) <= 0.0

MASTER_c_l_COST_Leaf3_AnoProfit_Ano2(None)_:  1.0 MASTER_EXPECTED_COST_Leaf3 - 1.0 MASTER_Leaf3_AnoProfit(Ano2) >= 0.0

MASTER_c_u_COST_Leaf3_AnoProfit_Ano2(None)_:  1.0 MASTER_EXPECTED_COST_Leaf3 - 1.0 MASTER_Leaf3_AnoProfit(Ano2) <= 0.0

MASTER_c_l_ForestDavis16_RootNode_delta_(TrackEighteen,Ano1)(None)_:  -1.0 ForestDavis16_delta((TrackEighteen,Ano1)) + 1.0 MASTER_RootNode_delta((TrackEighteen,Ano1)) >= 0.0

MASTER_c_u_ForestDavis16_RootNode_delta_(TrackEighteen,Ano1)(None)_:  -1.0 ForestDavis16_delta((TrackEighteen,Ano1)) + 1.0 MASTER_RootNode_delta((TrackEighteen,Ano1)) <= 0.0

MASTER_c_l_ForestDavis4_RootNode_z_(Exit1,Ano1)(None)_:  -1.0 ForestDavis4_z((Exit1,Ano1)) + 1.0 MASTER_RootNode_z((Exit1,Ano1)) >= 0.0

MASTER_c_u_ForestDavis4_RootNode_z_(Exit1,Ano1)(None)_:  -1.0 ForestDavis4_z((Exit1,Ano1)) + 1.0 MASTER_RootNode_z((Exit1,Ano1)) <= 0.0

MASTER_c_l_ForestDavis8_RootNode_AnoProfit_Ano1(None)_:  -1.0 ForestDavis8_AnoProfit(Ano1) + 1.0 MASTER_RootNode_AnoProfit(Ano1) >= 0.0

MASTER_c_u_ForestDavis8_RootNode_AnoProfit_Ano1(None)_:  -1.0 ForestDavis8_AnoProfit(Ano1) + 1.0 MASTER_RootNode_AnoProfit(Ano1) <= 0.0

MASTER_c_l_COST_Leaf1_AnoProfit_Ano2(None)_:  1.0 MASTER_EXPECTED_COST_Leaf1 - 1.0 MASTER_Leaf1_AnoProfit(Ano2) >= 0.0

MASTER_c_u_COST_Leaf1_AnoProfit_Ano2(None)_:  1.0 MASTER_EXPECTED_COST_Leaf1 - 1.0 MASTER_Leaf1_AnoProfit(Ano2) <= 0.0

MASTER_c_l_ForestDavis12_Leaf3_AnoProfit_Ano2(None)_:  -1.0 ForestDavis12_AnoProfit(Ano2) + 1.0 MASTER_Leaf3_AnoProfit(Ano2) >= 0.0

MASTER_c_u_ForestDavis12_Leaf3_AnoProfit_Ano2(None)_:  -1.0 ForestDavis12_AnoProfit(Ano2) + 1.0 MASTER_Leaf3_AnoProfit(Ano2) <= 0.0

MASTER_c_l_COST_RootNode_AnoProfit_Ano2(None)_:  -0.25 MASTER_EXPECTED_COST_Leaf1 - 0.25 MASTER_EXPECTED_COST_Leaf2 - 0.25 MASTER_EXPECTED_COST_Leaf3 - 0.25 MASTER_EXPECTED_COST_Leaf4 + 1.0 MASTER_EXPECTED_COST_RootNode 
- 1.0 MASTER_RootNode_AnoProfit(Ano1) >= 0.0

MASTER_c_u_COST_RootNode_AnoProfit_Ano2(None)_:  -0.25 MASTER_EXPECTED_COST_Leaf1 - 0.25 MASTER_EXPECTED_COST_Leaf2 - 0.25 MASTER_EXPECTED_COST_Leaf3 - 0.25 MASTER_EXPECTED_COST_Leaf4 + 1.0 MASTER_EXPECTED_COST_RootNode 
- 1.0 MASTER_RootNode_AnoProfit(Ano1) <= 0.0

MASTER_c_l_ForestDavis12_RootNode_delta_(TrackEighteen,Ano1)(None)_:  -1.0 ForestDavis12_delta((TrackEighteen,Ano1)) + 1.0 MASTER_RootNode_delta((TrackEighteen,Ano1)) >= 0.0

MASTER_c_u_ForestDavis12_RootNode_delta_(TrackEighteen,Ano1)(None)_:  -1.0 ForestDavis12_delta((TrackEighteen,Ano1)) + 1.0 MASTER_RootNode_delta((TrackEighteen,Ano1)) <= 0.0

MASTER_c_l_ForestDavis16_RootNode_z_(Exit1,Ano1)(None)_:  -1.0 ForestDavis16_z((Exit1,Ano1)) + 1.0 MASTER_RootNode_z((Exit1,Ano1)) >= 0.0

MASTER_c_u_ForestDavis16_RootNode_z_(Exit1,Ano1)(None)_:  -1.0 ForestDavis16_z((Exit1,Ano1)) + 1.0 MASTER_RootNode_z((Exit1,Ano1)) <= 0.0

MASTER_c_l_COST_Leaf2_AnoProfit_Ano2(None)_:  1.0 MASTER_EXPECTED_COST_Leaf2 - 1.0 MASTER_Leaf2_AnoProfit(Ano2) >= 0.0

MASTER_c_u_COST_Leaf2_AnoProfit_Ano2(None)_:  1.0 MASTER_EXPECTED_COST_Leaf2 - 1.0 MASTER_Leaf2_AnoProfit(Ano2) <= 0.0

MASTER_c_l_ForestDavis16_Leaf4_AnoProfit_Ano2(None)_:  -1.0 ForestDavis16_AnoProfit(Ano2) + 1.0 MASTER_Leaf4_AnoProfit(Ano2) >= 0.0

MASTER_c_u_ForestDavis16_Leaf4_AnoProfit_Ano2(None)_:  -1.0 ForestDavis16_AnoProfit(Ano2) + 1.0 MASTER_Leaf4_AnoProfit(Ano2) <= 0.0

c_e_ONE_VAR_CONSTANT: ONE_VAR_CONSTANT = 1.0

\ End constraint block for master 
\ Begin constraint block for scenario ForestDavis8
ForestDavis8_c_e_EnforceOriginFlowBalance((Origin5,Ano1))_:  15000.0 ForestDavis8_delta((TrackFourteen,Ano1)) + 17500.0 ForestDavis8_delta((TrackSeventeen,Ano1)) + 19950.0 ForestDavis8_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis8_f((Int1Org5P,Ano1)) - 1.0 ForestDavis8_f((Org5Exit1E,Ano1)) 
= 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin5,Ano2))_:  15700.0 ForestDavis8_delta((TrackFourteen,Ano2)) + 18760.0 ForestDavis8_delta((TrackSeventeen,Ano2)) + 20650.0 ForestDavis8_delta((TrackThirteen,Ano2)) + 1.0 ForestDavis8_f((Int1Org5P,Ano2)) - 1.0 ForestDavis8_f((Org5Exit1E,Ano2)) 
= 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin4,Ano1))_:  17500.0 ForestDavis8_delta((TrackFive,Ano1)) + 16500.0 ForestDavis8_delta((TrackNine,Ano1)) + 18750.0 ForestDavis8_delta((TrackTen,Ano1)) - 1.0 ForestDavis8_f((Org4Int1P,Ano1)) - 1.0 ForestDavis8_f((Org4Org9P,Ano1)) 
= 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin4,Ano2))_:  19460.0 ForestDavis8_delta((TrackFive,Ano2)) + 16940.0 ForestDavis8_delta((TrackNine,Ano2)) + 20700.0 ForestDavis8_delta((TrackTen,Ano2)) - 1.0 ForestDavis8_f((Org4Int1P,Ano2)) - 1.0 ForestDavis8_f((Org4Org9P,Ano2)) 
= 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin7,Ano1))_:  18000.0 ForestDavis8_delta((TrackTwenty,Ano1)) + 18750.0 ForestDavis8_delta((TrackTwentyFive,Ano1)) + 20000.0 ForestDavis8_delta((TrackTwentyFour,Ano1)) - 1.0 ForestDavis8_f((Org7Exit1P,Ano1)) - 1.0 ForestDavis8_f((Org7Int2E,Ano1)) 
= 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin7,Ano2))_:  18180.0 ForestDavis8_delta((TrackTwenty,Ano2)) + 19350.0 ForestDavis8_delta((TrackTwentyFive,Ano2)) + 20480.0 ForestDavis8_delta((TrackTwentyFour,Ano2)) - 1.0 ForestDavis8_f((Org7Exit1P,Ano2)) - 1.0 ForestDavis8_f((Org7Int2E,Ano2)) 
= 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin6,Ano1))_:  19800.0 ForestDavis8_delta((TrackSixteen,Ano1)) + 18750.0 ForestDavis8_delta((TrackTwentyOne,Ano1)) - 1.0 ForestDavis8_f((Org6Exit1P,Ano1)) = 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin6,Ano2))_:  19920.0 ForestDavis8_delta((TrackSixteen,Ano2)) + 20400.0 ForestDavis8_delta((TrackTwentyOne,Ano2)) - 1.0 ForestDavis8_f((Org6Exit1P,Ano2)) = 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin1,Ano1))_:  16500.0 ForestDavis8_delta((TrackOne,Ano1)) + 18750.0 ForestDavis8_delta((TrackSix,Ano1)) + 15000.0 ForestDavis8_delta((TrackTwo,Ano1)) - 1.0 ForestDavis8_f((Org1Int3P,Ano1)) - 1.0 ForestDavis8_f((Org1Org2P,Ano1)) 
- 1.0 ForestDavis8_f((Org1Org3P,Ano1)) = 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin1,Ano2))_:  17930.0 ForestDavis8_delta((TrackOne,Ano2)) + 19350.0 ForestDavis8_delta((TrackSix,Ano2)) + 16400.0 ForestDavis8_delta((TrackTwo,Ano2)) - 1.0 ForestDavis8_f((Org1Int3P,Ano2)) - 1.0 ForestDavis8_f((Org1Org2P,Ano2)) 
- 1.0 ForestDavis8_f((Org1Org3P,Ano2)) = 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin3,Ano1))_:  18000.0 ForestDavis8_delta((TrackEight,Ano1)) + 15000.0 ForestDavis8_delta((TrackFour,Ano1)) + 15000.0 ForestDavis8_delta((TrackThree,Ano1)) + 1.0 ForestDavis8_f((Org1Org3P,Ano1)) - 1.0 ForestDavis8_f((Org3Int1P,Ano1)) 
= 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin3,Ano2))_:  18180.0 ForestDavis8_delta((TrackEight,Ano2)) + 15100.0 ForestDavis8_delta((TrackFour,Ano2)) + 15900.0 ForestDavis8_delta((TrackThree,Ano2)) + 1.0 ForestDavis8_f((Org1Org3P,Ano2)) - 1.0 ForestDavis8_f((Org3Int1P,Ano2)) 
= 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin2,Ano1))_:  19800.0 ForestDavis8_delta((TrackEleven,Ano1)) + 18000.0 ForestDavis8_delta((TrackSeven,Ano1)) + 18000.0 ForestDavis8_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis8_f((Org1Org2P,Ano1)) - 1.0 ForestDavis8_f((Org2Exit1P,Ano1)) 
- 1.0 ForestDavis8_f((Org2Int3E,Ano1)) = 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin2,Ano2))_:  21480.0 ForestDavis8_delta((TrackEleven,Ano2)) + 18720.0 ForestDavis8_delta((TrackSeven,Ano2)) + 18720.0 ForestDavis8_delta((TrackTwelve,Ano2)) + 1.0 ForestDavis8_f((Org1Org2P,Ano2)) - 1.0 ForestDavis8_f((Org2Exit1P,Ano2)) 
- 1.0 ForestDavis8_f((Org2Int3E,Ano2)) = 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin9,Ano1))_:  19800.0 ForestDavis8_delta((TrackEighteen,Ano1)) + 18750.0 ForestDavis8_delta((TrackFifteen,Ano1)) + 15000.0 ForestDavis8_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis8_f((Org4Org9P,Ano1)) - 1.0 ForestDavis8_f((Org9Int2P,Ano1)) 
= 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin9,Ano2))_:  20400.0 ForestDavis8_delta((TrackEighteen,Ano2)) + 18900.0 ForestDavis8_delta((TrackFifteen,Ano2)) + 16400.0 ForestDavis8_delta((TrackNineteen,Ano2)) + 1.0 ForestDavis8_f((Org4Org9P,Ano2)) - 1.0 ForestDavis8_f((Org9Int2P,Ano2)) 
= 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin8,Ano1))_:  18000.0 ForestDavis8_delta((TrackTwentyThree,Ano1)) + 18750.0 ForestDavis8_delta((TrackTwentyTwo,Ano1)) - 1.0 ForestDavis8_f((Org8Exit1P,Ano1)) = 0.0

ForestDavis8_c_e_EnforceOriginFlowBalance((Origin8,Ano2))_:  18000.0 ForestDavis8_delta((TrackTwentyThree,Ano2)) + 19350.0 ForestDavis8_delta((TrackTwentyTwo,Ano2)) - 1.0 ForestDavis8_f((Org8Exit1P,Ano2)) = 0.0

ForestDavis8_c_l_EnforceWoodProductionBounds(Ano1)_:  1.0 ForestDavis8_z((Exit1,Ano1)) >= 30000.0

ForestDavis8_c_u_EnforceWoodProductionBounds(Ano1)_:  1.0 ForestDavis8_z((Exit1,Ano1)) <= 40000.0

ForestDavis8_c_l_EnforceWoodProductionBounds(Ano2)_:  1.0 ForestDavis8_z((Exit1,Ano2)) >= 15000.0

ForestDavis8_c_u_EnforceWoodProductionBounds(Ano2)_:  1.0 ForestDavis8_z((Exit1,Ano2)) <= 33000.0

ForestDavis8_c_e_EnforceDestinationFlowBalance((Exit1,Ano1))_:  -1.0 ForestDavis8_f((Int1Exit1P,Ano1)) - 1.0 ForestDavis8_f((Int2Exit1E,Ano1)) - 1.0 ForestDavis8_f((Int3Exit1E,Ano1)) - 1.0 ForestDavis8_f((Org2Exit1P,Ano1)) - 1.0 ForestDavis8_f((Org5Exit1E,Ano1)) 
- 1.0 ForestDavis8_f((Org6Exit1P,Ano1)) - 1.0 ForestDavis8_f((Org7Exit1P,Ano1)) - 1.0 ForestDavis8_f((Org8Exit1P,Ano1)) + 1.0 ForestDavis8_z((Exit1,Ano1)) = 0.0

ForestDavis8_c_e_EnforceDestinationFlowBalance((Exit1,Ano2))_:  -1.0 ForestDavis8_f((Int1Exit1P,Ano2)) - 1.0 ForestDavis8_f((Int2Exit1E,Ano2)) - 1.0 ForestDavis8_f((Int3Exit1E,Ano2)) - 1.0 ForestDavis8_f((Org2Exit1P,Ano2)) - 1.0 ForestDavis8_f((Org5Exit1E,Ano2)) 
- 1.0 ForestDavis8_f((Org6Exit1P,Ano2)) - 1.0 ForestDavis8_f((Org7Exit1P,Ano2)) - 1.0 ForestDavis8_f((Org8Exit1P,Ano2)) + 1.0 ForestDavis8_z((Exit1,Ano2)) = 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org1Org2P,Ano1))_:  1.0 ForestDavis8_f((Org1Org2P,Ano1)) - 15000.0 ForestDavis8_gamma((Org1Org2P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org1Org2P,Ano2))_:  1.0 ForestDavis8_f((Org1Org2P,Ano2)) - 16400.0 ForestDavis8_gamma((Org1Org2P,Ano1)) - 16400.0 ForestDavis8_gamma((Org1Org2P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org6Exit1P,Ano1))_:  1.0 ForestDavis8_f((Org6Exit1P,Ano1)) - 19800.0 ForestDavis8_gamma((Org6Exit1P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org6Exit1P,Ano2))_:  1.0 ForestDavis8_f((Org6Exit1P,Ano2)) - 20400.0 ForestDavis8_gamma((Org6Exit1P,Ano1)) - 20400.0 ForestDavis8_gamma((Org6Exit1P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org3Int1P,Ano1))_:  1.0 ForestDavis8_f((Org3Int1P,Ano1)) - 15000.0 ForestDavis8_gamma((Org3Int1P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org3Int1P,Ano2))_:  1.0 ForestDavis8_f((Org3Int1P,Ano2)) - 15100.0 ForestDavis8_gamma((Org3Int1P,Ano1)) - 15100.0 ForestDavis8_gamma((Org3Int1P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org4Int1P,Ano1))_:  1.0 ForestDavis8_f((Org4Int1P,Ano1)) - 17583.0 ForestDavis8_gamma((Org4Int1P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org4Int1P,Ano2))_:  1.0 ForestDavis8_f((Org4Int1P,Ano2)) - 19033.0 ForestDavis8_gamma((Org4Int1P,Ano1)) - 19033.0 ForestDavis8_gamma((Org4Int1P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org7Exit1P,Ano1))_:  1.0 ForestDavis8_f((Org7Exit1P,Ano1)) - 20000.0 ForestDavis8_gamma((Org7Exit1P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org7Exit1P,Ano2))_:  1.0 ForestDavis8_f((Org7Exit1P,Ano2)) - 20480.0 ForestDavis8_gamma((Org7Exit1P,Ano1)) - 20480.0 ForestDavis8_gamma((Org7Exit1P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org2Exit1P,Ano1))_:  1.0 ForestDavis8_f((Org2Exit1P,Ano1)) - 19800.0 ForestDavis8_gamma((Org2Exit1P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org2Exit1P,Ano2))_:  1.0 ForestDavis8_f((Org2Exit1P,Ano2)) - 21480.0 ForestDavis8_gamma((Org2Exit1P,Ano1)) - 21480.0 ForestDavis8_gamma((Org2Exit1P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org1Int3P,Ano1))_:  1.0 ForestDavis8_f((Org1Int3P,Ano1)) - 18750.0 ForestDavis8_gamma((Org1Int3P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org1Int3P,Ano2))_:  1.0 ForestDavis8_f((Org1Int3P,Ano2)) - 19350.0 ForestDavis8_gamma((Org1Int3P,Ano1)) - 19350.0 ForestDavis8_gamma((Org1Int3P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Int1Exit1P,Ano1))_:  1.0 ForestDavis8_f((Int1Exit1P,Ano1)) - 17583.0 ForestDavis8_gamma((Int1Exit1P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Int1Exit1P,Ano2))_:  1.0 ForestDavis8_f((Int1Exit1P,Ano2)) - 19033.0 ForestDavis8_gamma((Int1Exit1P,Ano1)) - 19033.0 ForestDavis8_gamma((Int1Exit1P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org1Org3P,Ano1))_:  1.0 ForestDavis8_f((Org1Org3P,Ano1)) - 18750.0 ForestDavis8_gamma((Org1Org3P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org1Org3P,Ano2))_:  1.0 ForestDavis8_f((Org1Org3P,Ano2)) - 19350.0 ForestDavis8_gamma((Org1Org3P,Ano1)) - 19350.0 ForestDavis8_gamma((Org1Org3P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org4Org9P,Ano1))_:  1.0 ForestDavis8_f((Org4Org9P,Ano1)) - 18750.0 ForestDavis8_gamma((Org4Org9P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org4Org9P,Ano2))_:  1.0 ForestDavis8_f((Org4Org9P,Ano2)) - 20700.0 ForestDavis8_gamma((Org4Org9P,Ano1)) - 20700.0 ForestDavis8_gamma((Org4Org9P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Int1Org5P,Ano1))_:  1.0 ForestDavis8_f((Int1Org5P,Ano1)) - 17583.0 ForestDavis8_gamma((Int1Org5P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Int1Org5P,Ano2))_:  1.0 ForestDavis8_f((Int1Org5P,Ano2)) - 19033.0 ForestDavis8_gamma((Int1Org5P,Ano1)) - 19033.0 ForestDavis8_gamma((Int1Org5P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org8Exit1P,Ano1))_:  1.0 ForestDavis8_f((Org8Exit1P,Ano1)) - 18750.0 ForestDavis8_gamma((Org8Exit1P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org8Exit1P,Ano2))_:  1.0 ForestDavis8_f((Org8Exit1P,Ano2)) - 19350.0 ForestDavis8_gamma((Org8Exit1P,Ano1)) - 19350.0 ForestDavis8_gamma((Org8Exit1P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org9Int2P,Ano1))_:  1.0 ForestDavis8_f((Org9Int2P,Ano1)) - 19800.0 ForestDavis8_gamma((Org9Int2P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Org9Int2P,Ano2))_:  1.0 ForestDavis8_f((Org9Int2P,Ano2)) - 20400.0 ForestDavis8_gamma((Org9Int2P,Ano1)) - 20400.0 ForestDavis8_gamma((Org9Int2P,Ano2)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Int1Int3P,Ano1))_:  1.0 ForestDavis8_f((Int1Int3P,Ano1)) - 17583.0 ForestDavis8_gamma((Int1Int3P,Ano1)) <= 0.0

ForestDavis8_c_u_EnforcePotentialRoadFlowCap((Int1Int3P,Ano2))_:  1.0 ForestDavis8_f((Int1Int3P,Ano2)) - 19033.0 ForestDavis8_gamma((Int1Int3P,Ano1)) - 19033.0 ForestDavis8_gamma((Int1Int3P,Ano2)) <= 0.0

ForestDavis8_c_e_EnforceIntersectionFlowBalance((Intersection1,Ano1))_:  -1.0 ForestDavis8_f((Int1Exit1P,Ano1)) - 1.0 ForestDavis8_f((Int1Int2E,Ano1)) - 1.0 ForestDavis8_f((Int1Int3P,Ano1)) - 1.0 ForestDavis8_f((Int1Org5P,Ano1)) + 1.0 ForestDavis8_f((Org3Int1P,Ano1)) 
+ 1.0 ForestDavis8_f((Org4Int1P,Ano1)) = 0.0

ForestDavis8_c_e_EnforceIntersectionFlowBalance((Intersection1,Ano2))_:  -1.0 ForestDavis8_f((Int1Exit1P,Ano2)) - 1.0 ForestDavis8_f((Int1Int2E,Ano2)) - 1.0 ForestDavis8_f((Int1Int3P,Ano2)) - 1.0 ForestDavis8_f((Int1Org5P,Ano2)) + 1.0 ForestDavis8_f((Org3Int1P,Ano2)) 
+ 1.0 ForestDavis8_f((Org4Int1P,Ano2)) = 0.0

ForestDavis8_c_e_EnforceIntersectionFlowBalance((Intersection2,Ano1))_:  1.0 ForestDavis8_f((Int1Int2E,Ano1)) - 1.0 ForestDavis8_f((Int2Exit1E,Ano1)) + 1.0 ForestDavis8_f((Org7Int2E,Ano1)) + 1.0 ForestDavis8_f((Org9Int2P,Ano1)) = 0.0

ForestDavis8_c_e_EnforceIntersectionFlowBalance((Intersection2,Ano2))_:  1.0 ForestDavis8_f((Int1Int2E,Ano2)) - 1.0 ForestDavis8_f((Int2Exit1E,Ano2)) + 1.0 ForestDavis8_f((Org7Int2E,Ano2)) + 1.0 ForestDavis8_f((Org9Int2P,Ano2)) = 0.0

ForestDavis8_c_e_EnforceIntersectionFlowBalance((Intersection3,Ano1))_:  1.0 ForestDavis8_f((Int1Int3P,Ano1)) - 1.0 ForestDavis8_f((Int3Exit1E,Ano1)) + 1.0 ForestDavis8_f((Org1Int3P,Ano1)) + 1.0 ForestDavis8_f((Org2Int3E,Ano1)) = 0.0

ForestDavis8_c_e_EnforceIntersectionFlowBalance((Intersection3,Ano2))_:  1.0 ForestDavis8_f((Int1Int3P,Ano2)) - 1.0 ForestDavis8_f((Int3Exit1E,Ano2)) + 1.0 ForestDavis8_f((Org1Int3P,Ano2)) + 1.0 ForestDavis8_f((Org2Int3E,Ano2)) = 0.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Int3Exit1E,Ano1))_:  1.0 ForestDavis8_f((Int3Exit1E,Ano1)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Int3Exit1E,Ano1))_:  1.0 ForestDavis8_f((Int3Exit1E,Ano1)) <= 17583.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Int3Exit1E,Ano2))_:  1.0 ForestDavis8_f((Int3Exit1E,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Int3Exit1E,Ano2))_:  1.0 ForestDavis8_f((Int3Exit1E,Ano2)) <= 18720.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Int1Int2E,Ano1))_:  1.0 ForestDavis8_f((Int1Int2E,Ano1)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Int1Int2E,Ano1))_:  1.0 ForestDavis8_f((Int1Int2E,Ano1)) <= 15000.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Int1Int2E,Ano2))_:  1.0 ForestDavis8_f((Int1Int2E,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Int1Int2E,Ano2))_:  1.0 ForestDavis8_f((Int1Int2E,Ano2)) <= 15100.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Org2Int3E,Ano1))_:  1.0 ForestDavis8_f((Org2Int3E,Ano1)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Org2Int3E,Ano1))_:  1.0 ForestDavis8_f((Org2Int3E,Ano1)) <= 18000.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Org2Int3E,Ano2))_:  1.0 ForestDavis8_f((Org2Int3E,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Org2Int3E,Ano2))_:  1.0 ForestDavis8_f((Org2Int3E,Ano2)) <= 18720.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Org7Int2E,Ano1))_:  1.0 ForestDavis8_f((Org7Int2E,Ano1)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Org7Int2E,Ano1))_:  1.0 ForestDavis8_f((Org7Int2E,Ano1)) <= 18000.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Org7Int2E,Ano2))_:  1.0 ForestDavis8_f((Org7Int2E,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Org7Int2E,Ano2))_:  1.0 ForestDavis8_f((Org7Int2E,Ano2)) <= 18180.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Org5Exit1E,Ano1))_:  1.0 ForestDavis8_f((Org5Exit1E,Ano1)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Org5Exit1E,Ano1))_:  1.0 ForestDavis8_f((Org5Exit1E,Ano1)) <= 15000.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Org5Exit1E,Ano2))_:  1.0 ForestDavis8_f((Org5Exit1E,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Org5Exit1E,Ano2))_:  1.0 ForestDavis8_f((Org5Exit1E,Ano2)) <= 15700.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Int2Exit1E,Ano1))_:  1.0 ForestDavis8_f((Int2Exit1E,Ano1)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Int2Exit1E,Ano1))_:  1.0 ForestDavis8_f((Int2Exit1E,Ano1)) <= 15000.0

ForestDavis8_c_l_EnforceExistingRoadCapacities((Int2Exit1E,Ano2))_:  1.0 ForestDavis8_f((Int2Exit1E,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceExistingRoadCapacities((Int2Exit1E,Ano2))_:  1.0 ForestDavis8_f((Int2Exit1E,Ano2)) <= 15100.0

ForestDavis8_c_l_EnforceOneHarvest(TrackNine)_:  1.0 ForestDavis8_delta((TrackNine,Ano1)) + 1.0 ForestDavis8_delta((TrackNine,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackNine)_:  1.0 ForestDavis8_delta((TrackNine,Ano1)) + 1.0 ForestDavis8_delta((TrackNine,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackTwentyThree)_:  1.0 ForestDavis8_delta((TrackTwentyThree,Ano1)) + 1.0 ForestDavis8_delta((TrackTwentyThree,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackTwentyThree)_:  1.0 ForestDavis8_delta((TrackTwentyThree,Ano1)) + 1.0 ForestDavis8_delta((TrackTwentyThree,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackOne)_:  1.0 ForestDavis8_delta((TrackOne,Ano1)) + 1.0 ForestDavis8_delta((TrackOne,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackOne)_:  1.0 ForestDavis8_delta((TrackOne,Ano1)) + 1.0 ForestDavis8_delta((TrackOne,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackEleven)_:  1.0 ForestDavis8_delta((TrackEleven,Ano1)) + 1.0 ForestDavis8_delta((TrackEleven,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackEleven)_:  1.0 ForestDavis8_delta((TrackEleven,Ano1)) + 1.0 ForestDavis8_delta((TrackEleven,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackThree)_:  1.0 ForestDavis8_delta((TrackThree,Ano1)) + 1.0 ForestDavis8_delta((TrackThree,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackThree)_:  1.0 ForestDavis8_delta((TrackThree,Ano1)) + 1.0 ForestDavis8_delta((TrackThree,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackTwentyFour)_:  1.0 ForestDavis8_delta((TrackTwentyFour,Ano1)) + 1.0 ForestDavis8_delta((TrackTwentyFour,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackTwentyFour)_:  1.0 ForestDavis8_delta((TrackTwentyFour,Ano1)) + 1.0 ForestDavis8_delta((TrackTwentyFour,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackSeventeen)_:  1.0 ForestDavis8_delta((TrackSeventeen,Ano1)) + 1.0 ForestDavis8_delta((TrackSeventeen,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackSeventeen)_:  1.0 ForestDavis8_delta((TrackSeventeen,Ano1)) + 1.0 ForestDavis8_delta((TrackSeventeen,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackTwelve)_:  1.0 ForestDavis8_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis8_delta((TrackTwelve,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackTwelve)_:  1.0 ForestDavis8_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis8_delta((TrackTwelve,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackNineteen)_:  1.0 ForestDavis8_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis8_delta((TrackNineteen,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackNineteen)_:  1.0 ForestDavis8_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis8_delta((TrackNineteen,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackTen)_:  1.0 ForestDavis8_delta((TrackTen,Ano1)) + 1.0 ForestDavis8_delta((TrackTen,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackTen)_:  1.0 ForestDavis8_delta((TrackTen,Ano1)) + 1.0 ForestDavis8_delta((TrackTen,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackThirteen)_:  1.0 ForestDavis8_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis8_delta((TrackThirteen,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackThirteen)_:  1.0 ForestDavis8_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis8_delta((TrackThirteen,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackTwenty)_:  1.0 ForestDavis8_delta((TrackTwenty,Ano1)) + 1.0 ForestDavis8_delta((TrackTwenty,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackTwenty)_:  1.0 ForestDavis8_delta((TrackTwenty,Ano1)) + 1.0 ForestDavis8_delta((TrackTwenty,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackTwentyTwo)_:  1.0 ForestDavis8_delta((TrackTwentyTwo,Ano1)) + 1.0 ForestDavis8_delta((TrackTwentyTwo,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackTwentyTwo)_:  1.0 ForestDavis8_delta((TrackTwentyTwo,Ano1)) + 1.0 ForestDavis8_delta((TrackTwentyTwo,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackSixteen)_:  1.0 ForestDavis8_delta((TrackSixteen,Ano1)) + 1.0 ForestDavis8_delta((TrackSixteen,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackSixteen)_:  1.0 ForestDavis8_delta((TrackSixteen,Ano1)) + 1.0 ForestDavis8_delta((TrackSixteen,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackTwo)_:  1.0 ForestDavis8_delta((TrackTwo,Ano1)) + 1.0 ForestDavis8_delta((TrackTwo,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackTwo)_:  1.0 ForestDavis8_delta((TrackTwo,Ano1)) + 1.0 ForestDavis8_delta((TrackTwo,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackSix)_:  1.0 ForestDavis8_delta((TrackSix,Ano1)) + 1.0 ForestDavis8_delta((TrackSix,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackSix)_:  1.0 ForestDavis8_delta((TrackSix,Ano1)) + 1.0 ForestDavis8_delta((TrackSix,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackSeven)_:  1.0 ForestDavis8_delta((TrackSeven,Ano1)) + 1.0 ForestDavis8_delta((TrackSeven,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackSeven)_:  1.0 ForestDavis8_delta((TrackSeven,Ano1)) + 1.0 ForestDavis8_delta((TrackSeven,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackFifteen)_:  1.0 ForestDavis8_delta((TrackFifteen,Ano1)) + 1.0 ForestDavis8_delta((TrackFifteen,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackFifteen)_:  1.0 ForestDavis8_delta((TrackFifteen,Ano1)) + 1.0 ForestDavis8_delta((TrackFifteen,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackFour)_:  1.0 ForestDavis8_delta((TrackFour,Ano1)) + 1.0 ForestDavis8_delta((TrackFour,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackFour)_:  1.0 ForestDavis8_delta((TrackFour,Ano1)) + 1.0 ForestDavis8_delta((TrackFour,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackFourteen)_:  1.0 ForestDavis8_delta((TrackFourteen,Ano1)) + 1.0 ForestDavis8_delta((TrackFourteen,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackFourteen)_:  1.0 ForestDavis8_delta((TrackFourteen,Ano1)) + 1.0 ForestDavis8_delta((TrackFourteen,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackTwentyOne)_:  1.0 ForestDavis8_delta((TrackTwentyOne,Ano1)) + 1.0 ForestDavis8_delta((TrackTwentyOne,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackTwentyOne)_:  1.0 ForestDavis8_delta((TrackTwentyOne,Ano1)) + 1.0 ForestDavis8_delta((TrackTwentyOne,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackEighteen)_:  1.0 ForestDavis8_delta((TrackEighteen,Ano1)) + 1.0 ForestDavis8_delta((TrackEighteen,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackEighteen)_:  1.0 ForestDavis8_delta((TrackEighteen,Ano1)) + 1.0 ForestDavis8_delta((TrackEighteen,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackFive)_:  1.0 ForestDavis8_delta((TrackFive,Ano1)) + 1.0 ForestDavis8_delta((TrackFive,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackFive)_:  1.0 ForestDavis8_delta((TrackFive,Ano1)) + 1.0 ForestDavis8_delta((TrackFive,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackTwentyFive)_:  1.0 ForestDavis8_delta((TrackTwentyFive,Ano1)) + 1.0 ForestDavis8_delta((TrackTwentyFive,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackTwentyFive)_:  1.0 ForestDavis8_delta((TrackTwentyFive,Ano1)) + 1.0 ForestDavis8_delta((TrackTwentyFive,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOneHarvest(TrackEight)_:  1.0 ForestDavis8_delta((TrackEight,Ano1)) + 1.0 ForestDavis8_delta((TrackEight,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOneHarvest(TrackEight)_:  1.0 ForestDavis8_delta((TrackEight,Ano1)) + 1.0 ForestDavis8_delta((TrackEight,Ano2)) <= 1.0

ForestDavis8_c_e_ComputeStageProfit(Ano1)_:  1.0 ForestDavis8_AnoProfit(Ano1) + 711000.0 ForestDavis8_delta((TrackEight,Ano1)) + 447000.0 ForestDavis8_delta((TrackEighteen,Ano1)) + 507000.0 ForestDavis8_delta((TrackEleven,Ano1)) + 618750.0 ForestDavis8_delta((TrackFifteen,Ano1)) 
+ 560000.0 ForestDavis8_delta((TrackFive,Ano1)) + 375000.0 ForestDavis8_delta((TrackFour,Ano1)) + 387500.0 ForestDavis8_delta((TrackFourteen,Ano1)) + 453750.0 ForestDavis8_delta((TrackNine,Ano1)) + 275000.0 ForestDavis8_delta((TrackNineteen,Ano1)) 
+ 412500.0 ForestDavis8_delta((TrackOne,Ano1)) + 461250.0 ForestDavis8_delta((TrackSeven,Ano1)) + 535500.0 ForestDavis8_delta((TrackSeventeen,Ano1)) + 656250.0 ForestDavis8_delta((TrackSix,Ano1)) + 561000.0 ForestDavis8_delta((TrackSixteen,Ano1)) 
+ 656250.0 ForestDavis8_delta((TrackTen,Ano1)) + 386750.0 ForestDavis8_delta((TrackThirteen,Ano1)) + 375000.0 ForestDavis8_delta((TrackThree,Ano1)) + 630000.0 ForestDavis8_delta((TrackTwelve,Ano1)) + 326250.0 ForestDavis8_delta((TrackTwenty,Ano1)) 
+ 393750.0 ForestDavis8_delta((TrackTwentyFive,Ano1)) + 330000.0 ForestDavis8_delta((TrackTwentyFour,Ano1)) + 468750.0 ForestDavis8_delta((TrackTwentyOne,Ano1)) + 315000.0 ForestDavis8_delta((TrackTwentyThree,Ano1)) + 431250.0 ForestDavis8_delta((TrackTwentyTwo,Ano1)) 
+ 400000.0 ForestDavis8_delta((TrackTwo,Ano1)) + 20.0 ForestDavis8_f((Int1Exit1P,Ano1)) + 17.0 ForestDavis8_f((Int1Int2E,Ano1)) + 14.0 ForestDavis8_f((Int1Int3P,Ano1)) + 10.0 ForestDavis8_f((Int1Org5P,Ano1)) 
+ 8.0 ForestDavis8_f((Int2Exit1E,Ano1)) + 15.0 ForestDavis8_f((Int3Exit1E,Ano1)) + 10.0 ForestDavis8_f((Org1Int3P,Ano1)) + 5.0 ForestDavis8_f((Org1Org2P,Ano1)) + 14.0 ForestDavis8_f((Org1Org3P,Ano1)) 
+ 21.0 ForestDavis8_f((Org2Exit1P,Ano1)) + 5.0 ForestDavis8_f((Org2Int3E,Ano1)) + 5.0 ForestDavis8_f((Org3Int1P,Ano1)) + 8.0 ForestDavis8_f((Org4Int1P,Ano1)) + 15.0 ForestDavis8_f((Org4Org9P,Ano1)) 
+ 12.0 ForestDavis8_f((Org5Exit1E,Ano1)) + 12.0 ForestDavis8_f((Org6Exit1P,Ano1)) + 15.0 ForestDavis8_f((Org7Exit1P,Ano1)) + 8.0 ForestDavis8_f((Org7Int2E,Ano1)) + 5.0 ForestDavis8_f((Org8Exit1P,Ano1)) 
+ 8.0 ForestDavis8_f((Org9Int2P,Ano1)) + 1800.0 ForestDavis8_gamma((Int1Exit1P,Ano1)) + 1750.0 ForestDavis8_gamma((Int1Int3P,Ano1)) + 1050.0 ForestDavis8_gamma((Int1Org5P,Ano1)) + 1110.0 ForestDavis8_gamma((Org1Int3P,Ano1)) 
+ 900.0 ForestDavis8_gamma((Org1Org2P,Ano1)) + 1200.0 ForestDavis8_gamma((Org1Org3P,Ano1)) + 2840.0 ForestDavis8_gamma((Org2Exit1P,Ano1)) + 900.0 ForestDavis8_gamma((Org3Int1P,Ano1)) + 1050.0 ForestDavis8_gamma((Org4Int1P,Ano1)) 
+ 1750.0 ForestDavis8_gamma((Org4Org9P,Ano1)) + 1550.0 ForestDavis8_gamma((Org6Exit1P,Ano1)) + 1750.0 ForestDavis8_gamma((Org7Exit1P,Ano1)) + 990.0 ForestDavis8_gamma((Org8Exit1P,Ano1)) + 1200.0 ForestDavis8_gamma((Org9Int2P,Ano1)) 
- 45.0 ForestDavis8_z((Exit1,Ano1)) = 0.0

ForestDavis8_c_e_ComputeStageProfit(Ano2)_:  1.0 ForestDavis8_AnoProfit(Ano2) + 673560.0 ForestDavis8_delta((TrackEight,Ano2)) + 442320.0 ForestDavis8_delta((TrackEighteen,Ano2)) + 513120.0 ForestDavis8_delta((TrackEleven,Ano2)) + 590250.0 ForestDavis8_delta((TrackFifteen,Ano2)) 
+ 562380.0 ForestDavis8_delta((TrackFive,Ano2)) + 362900.0 ForestDavis8_delta((TrackFour,Ano2)) + 383200.0 ForestDavis8_delta((TrackFourteen,Ano2)) + 441650.0 ForestDavis8_delta((TrackNine,Ano2)) + 291500.0 ForestDavis8_delta((TrackNineteen,Ano2)) 
+ 418990.0 ForestDavis8_delta((TrackOne,Ano2)) + 454680.0 ForestDavis8_delta((TrackSeven,Ano2)) + 529620.0 ForestDavis8_delta((TrackSeventeen,Ano2)) + 631200.0 ForestDavis8_delta((TrackSix,Ano2)) + 538800.0 ForestDavis8_delta((TrackSixteen,Ano2)) 
+ 651450.0 ForestDavis8_delta((TrackTen,Ano2)) + 389270.0 ForestDavis8_delta((TrackThirteen,Ano2)) + 374900.0 ForestDavis8_delta((TrackThree,Ano2)) + 608040.0 ForestDavis8_delta((TrackTwelve,Ano2)) + 323820.0 ForestDavis8_delta((TrackTwenty,Ano2)) 
+ 392550.0 ForestDavis8_delta((TrackTwentyFive,Ano2)) + 334480.0 ForestDavis8_delta((TrackTwentyFour,Ano2)) + 476400.0 ForestDavis8_delta((TrackTwentyOne,Ano2)) + 310950.0 ForestDavis8_delta((TrackTwentyThree,Ano2)) + 426600.0 ForestDavis8_delta((TrackTwentyTwo,Ano2)) 
+ 405100.0 ForestDavis8_delta((TrackTwo,Ano2)) + 20.0 ForestDavis8_f((Int1Exit1P,Ano2)) + 17.0 ForestDavis8_f((Int1Int2E,Ano2)) + 14.0 ForestDavis8_f((Int1Int3P,Ano2)) + 10.0 ForestDavis8_f((Int1Org5P,Ano2)) 
+ 8.0 ForestDavis8_f((Int2Exit1E,Ano2)) + 15.0 ForestDavis8_f((Int3Exit1E,Ano2)) + 10.0 ForestDavis8_f((Org1Int3P,Ano2)) + 5.0 ForestDavis8_f((Org1Org2P,Ano2)) + 14.0 ForestDavis8_f((Org1Org3P,Ano2)) 
+ 21.0 ForestDavis8_f((Org2Exit1P,Ano2)) + 5.0 ForestDavis8_f((Org2Int3E,Ano2)) + 5.0 ForestDavis8_f((Org3Int1P,Ano2)) + 8.0 ForestDavis8_f((Org4Int1P,Ano2)) + 15.0 ForestDavis8_f((Org4Org9P,Ano2)) 
+ 12.0 ForestDavis8_f((Org5Exit1E,Ano2)) + 12.0 ForestDavis8_f((Org6Exit1P,Ano2)) + 15.0 ForestDavis8_f((Org7Exit1P,Ano2)) + 8.0 ForestDavis8_f((Org7Int2E,Ano2)) + 5.0 ForestDavis8_f((Org8Exit1P,Ano2)) 
+ 8.0 ForestDavis8_f((Org9Int2P,Ano2)) + 1636.0 ForestDavis8_gamma((Int1Exit1P,Ano2)) + 1591.0 ForestDavis8_gamma((Int1Int3P,Ano2)) + 955.0 ForestDavis8_gamma((Int1Org5P,Ano2)) + 1009.0 ForestDavis8_gamma((Org1Int3P,Ano2)) 
+ 818.0 ForestDavis8_gamma((Org1Org2P,Ano2)) + 1091.0 ForestDavis8_gamma((Org1Org3P,Ano2)) + 2582.0 ForestDavis8_gamma((Org2Exit1P,Ano2)) + 818.0 ForestDavis8_gamma((Org3Int1P,Ano2)) + 955.0 ForestDavis8_gamma((Org4Int1P,Ano2)) 
+ 1591.0 ForestDavis8_gamma((Org4Org9P,Ano2)) + 1409.0 ForestDavis8_gamma((Org6Exit1P,Ano2)) + 1591.0 ForestDavis8_gamma((Org7Exit1P,Ano2)) + 900.0 ForestDavis8_gamma((Org8Exit1P,Ano2)) + 1091.0 ForestDavis8_gamma((Org9Int2P,Ano2)) 
- 45.0 ForestDavis8_z((Exit1,Ano2)) = 0.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org1Org2P)_:  1.0 ForestDavis8_gamma((Org1Org2P,Ano1)) + 1.0 ForestDavis8_gamma((Org1Org2P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org1Org2P)_:  1.0 ForestDavis8_gamma((Org1Org2P,Ano1)) + 1.0 ForestDavis8_gamma((Org1Org2P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org6Exit1P)_:  1.0 ForestDavis8_gamma((Org6Exit1P,Ano1)) + 1.0 ForestDavis8_gamma((Org6Exit1P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org6Exit1P)_:  1.0 ForestDavis8_gamma((Org6Exit1P,Ano1)) + 1.0 ForestDavis8_gamma((Org6Exit1P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org3Int1P)_:  1.0 ForestDavis8_gamma((Org3Int1P,Ano1)) + 1.0 ForestDavis8_gamma((Org3Int1P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org3Int1P)_:  1.0 ForestDavis8_gamma((Org3Int1P,Ano1)) + 1.0 ForestDavis8_gamma((Org3Int1P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org4Int1P)_:  1.0 ForestDavis8_gamma((Org4Int1P,Ano1)) + 1.0 ForestDavis8_gamma((Org4Int1P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org4Int1P)_:  1.0 ForestDavis8_gamma((Org4Int1P,Ano1)) + 1.0 ForestDavis8_gamma((Org4Int1P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org7Exit1P)_:  1.0 ForestDavis8_gamma((Org7Exit1P,Ano1)) + 1.0 ForestDavis8_gamma((Org7Exit1P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org7Exit1P)_:  1.0 ForestDavis8_gamma((Org7Exit1P,Ano1)) + 1.0 ForestDavis8_gamma((Org7Exit1P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org2Exit1P)_:  1.0 ForestDavis8_gamma((Org2Exit1P,Ano1)) + 1.0 ForestDavis8_gamma((Org2Exit1P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org2Exit1P)_:  1.0 ForestDavis8_gamma((Org2Exit1P,Ano1)) + 1.0 ForestDavis8_gamma((Org2Exit1P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org1Int3P)_:  1.0 ForestDavis8_gamma((Org1Int3P,Ano1)) + 1.0 ForestDavis8_gamma((Org1Int3P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org1Int3P)_:  1.0 ForestDavis8_gamma((Org1Int3P,Ano1)) + 1.0 ForestDavis8_gamma((Org1Int3P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Int1Exit1P)_:  1.0 ForestDavis8_gamma((Int1Exit1P,Ano1)) + 1.0 ForestDavis8_gamma((Int1Exit1P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Int1Exit1P)_:  1.0 ForestDavis8_gamma((Int1Exit1P,Ano1)) + 1.0 ForestDavis8_gamma((Int1Exit1P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org1Org3P)_:  1.0 ForestDavis8_gamma((Org1Org3P,Ano1)) + 1.0 ForestDavis8_gamma((Org1Org3P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org1Org3P)_:  1.0 ForestDavis8_gamma((Org1Org3P,Ano1)) + 1.0 ForestDavis8_gamma((Org1Org3P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org4Org9P)_:  1.0 ForestDavis8_gamma((Org4Org9P,Ano1)) + 1.0 ForestDavis8_gamma((Org4Org9P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org4Org9P)_:  1.0 ForestDavis8_gamma((Org4Org9P,Ano1)) + 1.0 ForestDavis8_gamma((Org4Org9P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Int1Org5P)_:  1.0 ForestDavis8_gamma((Int1Org5P,Ano1)) + 1.0 ForestDavis8_gamma((Int1Org5P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Int1Org5P)_:  1.0 ForestDavis8_gamma((Int1Org5P,Ano1)) + 1.0 ForestDavis8_gamma((Int1Org5P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org8Exit1P)_:  1.0 ForestDavis8_gamma((Org8Exit1P,Ano1)) + 1.0 ForestDavis8_gamma((Org8Exit1P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org8Exit1P)_:  1.0 ForestDavis8_gamma((Org8Exit1P,Ano1)) + 1.0 ForestDavis8_gamma((Org8Exit1P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Org9Int2P)_:  1.0 ForestDavis8_gamma((Org9Int2P,Ano1)) + 1.0 ForestDavis8_gamma((Org9Int2P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Org9Int2P)_:  1.0 ForestDavis8_gamma((Org9Int2P,Ano1)) + 1.0 ForestDavis8_gamma((Org9Int2P,Ano2)) <= 1.0

ForestDavis8_c_l_EnforceOnePotentialRoad(Int1Int3P)_:  1.0 ForestDavis8_gamma((Int1Int3P,Ano1)) + 1.0 ForestDavis8_gamma((Int1Int3P,Ano2)) >= 0.0

ForestDavis8_c_u_EnforceOnePotentialRoad(Int1Int3P)_:  1.0 ForestDavis8_gamma((Int1Int3P,Ano1)) + 1.0 ForestDavis8_gamma((Int1Int3P,Ano2)) <= 1.0

c_e_ONE_VAR_CONSTANT: ONE_VAR_CONSTANT = 1.0

\ End constraint block for scenario ForestDavis8

\ Begin constraint block for scenario ForestDavis12
ForestDavis12_c_e_EnforceOriginFlowBalance((Origin5,Ano1))_:  15000.0 ForestDavis12_delta((TrackFourteen,Ano1)) + 17500.0 ForestDavis12_delta((TrackSeventeen,Ano1)) + 19950.0 ForestDavis12_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis12_f((Int1Org5P,Ano1)) - 1.0 ForestDavis12_f((Org5Exit1E,Ano1)) 
= 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin5,Ano2))_:  15700.0 ForestDavis12_delta((TrackFourteen,Ano2)) + 18760.0 ForestDavis12_delta((TrackSeventeen,Ano2)) + 20650.0 ForestDavis12_delta((TrackThirteen,Ano2)) + 1.0 ForestDavis12_f((Int1Org5P,Ano2)) - 1.0 ForestDavis12_f((Org5Exit1E,Ano2)) 
= 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin4,Ano1))_:  17500.0 ForestDavis12_delta((TrackFive,Ano1)) + 16500.0 ForestDavis12_delta((TrackNine,Ano1)) + 18750.0 ForestDavis12_delta((TrackTen,Ano1)) - 1.0 ForestDavis12_f((Org4Int1P,Ano1)) - 1.0 ForestDavis12_f((Org4Org9P,Ano1)) 
= 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin4,Ano2))_:  19460.0 ForestDavis12_delta((TrackFive,Ano2)) + 16940.0 ForestDavis12_delta((TrackNine,Ano2)) + 20700.0 ForestDavis12_delta((TrackTen,Ano2)) - 1.0 ForestDavis12_f((Org4Int1P,Ano2)) - 1.0 ForestDavis12_f((Org4Org9P,Ano2)) 
= 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin7,Ano1))_:  18000.0 ForestDavis12_delta((TrackTwenty,Ano1)) + 18750.0 ForestDavis12_delta((TrackTwentyFive,Ano1)) + 20000.0 ForestDavis12_delta((TrackTwentyFour,Ano1)) - 1.0 ForestDavis12_f((Org7Exit1P,Ano1)) - 1.0 ForestDavis12_f((Org7Int2E,Ano1)) 
= 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin7,Ano2))_:  18180.0 ForestDavis12_delta((TrackTwenty,Ano2)) + 19350.0 ForestDavis12_delta((TrackTwentyFive,Ano2)) + 20480.0 ForestDavis12_delta((TrackTwentyFour,Ano2)) - 1.0 ForestDavis12_f((Org7Exit1P,Ano2)) - 1.0 ForestDavis12_f((Org7Int2E,Ano2)) 
= 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin6,Ano1))_:  19800.0 ForestDavis12_delta((TrackSixteen,Ano1)) + 18750.0 ForestDavis12_delta((TrackTwentyOne,Ano1)) - 1.0 ForestDavis12_f((Org6Exit1P,Ano1)) = 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin6,Ano2))_:  19920.0 ForestDavis12_delta((TrackSixteen,Ano2)) + 20400.0 ForestDavis12_delta((TrackTwentyOne,Ano2)) - 1.0 ForestDavis12_f((Org6Exit1P,Ano2)) = 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin1,Ano1))_:  16500.0 ForestDavis12_delta((TrackOne,Ano1)) + 18750.0 ForestDavis12_delta((TrackSix,Ano1)) + 15000.0 ForestDavis12_delta((TrackTwo,Ano1)) - 1.0 ForestDavis12_f((Org1Int3P,Ano1)) - 1.0 ForestDavis12_f((Org1Org2P,Ano1)) 
- 1.0 ForestDavis12_f((Org1Org3P,Ano1)) = 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin1,Ano2))_:  17930.0 ForestDavis12_delta((TrackOne,Ano2)) + 19350.0 ForestDavis12_delta((TrackSix,Ano2)) + 16400.0 ForestDavis12_delta((TrackTwo,Ano2)) - 1.0 ForestDavis12_f((Org1Int3P,Ano2)) - 1.0 ForestDavis12_f((Org1Org2P,Ano2)) 
- 1.0 ForestDavis12_f((Org1Org3P,Ano2)) = 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin3,Ano1))_:  18000.0 ForestDavis12_delta((TrackEight,Ano1)) + 15000.0 ForestDavis12_delta((TrackFour,Ano1)) + 15000.0 ForestDavis12_delta((TrackThree,Ano1)) + 1.0 ForestDavis12_f((Org1Org3P,Ano1)) - 1.0 ForestDavis12_f((Org3Int1P,Ano1)) 
= 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin3,Ano2))_:  18180.0 ForestDavis12_delta((TrackEight,Ano2)) + 15100.0 ForestDavis12_delta((TrackFour,Ano2)) + 15900.0 ForestDavis12_delta((TrackThree,Ano2)) + 1.0 ForestDavis12_f((Org1Org3P,Ano2)) - 1.0 ForestDavis12_f((Org3Int1P,Ano2)) 
= 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin2,Ano1))_:  19800.0 ForestDavis12_delta((TrackEleven,Ano1)) + 18000.0 ForestDavis12_delta((TrackSeven,Ano1)) + 18000.0 ForestDavis12_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis12_f((Org1Org2P,Ano1)) - 1.0 ForestDavis12_f((Org2Exit1P,Ano1)) 
- 1.0 ForestDavis12_f((Org2Int3E,Ano1)) = 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin2,Ano2))_:  21480.0 ForestDavis12_delta((TrackEleven,Ano2)) + 18720.0 ForestDavis12_delta((TrackSeven,Ano2)) + 18720.0 ForestDavis12_delta((TrackTwelve,Ano2)) + 1.0 ForestDavis12_f((Org1Org2P,Ano2)) - 1.0 ForestDavis12_f((Org2Exit1P,Ano2)) 
- 1.0 ForestDavis12_f((Org2Int3E,Ano2)) = 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin9,Ano1))_:  19800.0 ForestDavis12_delta((TrackEighteen,Ano1)) + 18750.0 ForestDavis12_delta((TrackFifteen,Ano1)) + 15000.0 ForestDavis12_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis12_f((Org4Org9P,Ano1)) - 1.0 ForestDavis12_f((Org9Int2P,Ano1)) 
= 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin9,Ano2))_:  20400.0 ForestDavis12_delta((TrackEighteen,Ano2)) + 18900.0 ForestDavis12_delta((TrackFifteen,Ano2)) + 16400.0 ForestDavis12_delta((TrackNineteen,Ano2)) + 1.0 ForestDavis12_f((Org4Org9P,Ano2)) - 1.0 ForestDavis12_f((Org9Int2P,Ano2)) 
= 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin8,Ano1))_:  18000.0 ForestDavis12_delta((TrackTwentyThree,Ano1)) + 18750.0 ForestDavis12_delta((TrackTwentyTwo,Ano1)) - 1.0 ForestDavis12_f((Org8Exit1P,Ano1)) = 0.0

ForestDavis12_c_e_EnforceOriginFlowBalance((Origin8,Ano2))_:  18000.0 ForestDavis12_delta((TrackTwentyThree,Ano2)) + 19350.0 ForestDavis12_delta((TrackTwentyTwo,Ano2)) - 1.0 ForestDavis12_f((Org8Exit1P,Ano2)) = 0.0

ForestDavis12_c_l_EnforceWoodProductionBounds(Ano1)_:  1.0 ForestDavis12_z((Exit1,Ano1)) >= 30000.0

ForestDavis12_c_u_EnforceWoodProductionBounds(Ano1)_:  1.0 ForestDavis12_z((Exit1,Ano1)) <= 40000.0

ForestDavis12_c_l_EnforceWoodProductionBounds(Ano2)_:  1.0 ForestDavis12_z((Exit1,Ano2)) >= 15000.0

ForestDavis12_c_u_EnforceWoodProductionBounds(Ano2)_:  1.0 ForestDavis12_z((Exit1,Ano2)) <= 33000.0

ForestDavis12_c_e_EnforceDestinationFlowBalance((Exit1,Ano1))_:  -1.0 ForestDavis12_f((Int1Exit1P,Ano1)) - 1.0 ForestDavis12_f((Int2Exit1E,Ano1)) - 1.0 ForestDavis12_f((Int3Exit1E,Ano1)) - 1.0 ForestDavis12_f((Org2Exit1P,Ano1)) - 1.0 ForestDavis12_f((Org5Exit1E,Ano1)) 
- 1.0 ForestDavis12_f((Org6Exit1P,Ano1)) - 1.0 ForestDavis12_f((Org7Exit1P,Ano1)) - 1.0 ForestDavis12_f((Org8Exit1P,Ano1)) + 1.0 ForestDavis12_z((Exit1,Ano1)) = 0.0

ForestDavis12_c_e_EnforceDestinationFlowBalance((Exit1,Ano2))_:  -1.0 ForestDavis12_f((Int1Exit1P,Ano2)) - 1.0 ForestDavis12_f((Int2Exit1E,Ano2)) - 1.0 ForestDavis12_f((Int3Exit1E,Ano2)) - 1.0 ForestDavis12_f((Org2Exit1P,Ano2)) - 1.0 ForestDavis12_f((Org5Exit1E,Ano2)) 
- 1.0 ForestDavis12_f((Org6Exit1P,Ano2)) - 1.0 ForestDavis12_f((Org7Exit1P,Ano2)) - 1.0 ForestDavis12_f((Org8Exit1P,Ano2)) + 1.0 ForestDavis12_z((Exit1,Ano2)) = 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org1Org2P,Ano1))_:  1.0 ForestDavis12_f((Org1Org2P,Ano1)) - 15000.0 ForestDavis12_gamma((Org1Org2P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org1Org2P,Ano2))_:  1.0 ForestDavis12_f((Org1Org2P,Ano2)) - 16400.0 ForestDavis12_gamma((Org1Org2P,Ano1)) - 16400.0 ForestDavis12_gamma((Org1Org2P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org6Exit1P,Ano1))_:  1.0 ForestDavis12_f((Org6Exit1P,Ano1)) - 19800.0 ForestDavis12_gamma((Org6Exit1P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org6Exit1P,Ano2))_:  1.0 ForestDavis12_f((Org6Exit1P,Ano2)) - 20400.0 ForestDavis12_gamma((Org6Exit1P,Ano1)) - 20400.0 ForestDavis12_gamma((Org6Exit1P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org3Int1P,Ano1))_:  1.0 ForestDavis12_f((Org3Int1P,Ano1)) - 15000.0 ForestDavis12_gamma((Org3Int1P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org3Int1P,Ano2))_:  1.0 ForestDavis12_f((Org3Int1P,Ano2)) - 15100.0 ForestDavis12_gamma((Org3Int1P,Ano1)) - 15100.0 ForestDavis12_gamma((Org3Int1P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org4Int1P,Ano1))_:  1.0 ForestDavis12_f((Org4Int1P,Ano1)) - 17583.0 ForestDavis12_gamma((Org4Int1P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org4Int1P,Ano2))_:  1.0 ForestDavis12_f((Org4Int1P,Ano2)) - 19033.0 ForestDavis12_gamma((Org4Int1P,Ano1)) - 19033.0 ForestDavis12_gamma((Org4Int1P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org7Exit1P,Ano1))_:  1.0 ForestDavis12_f((Org7Exit1P,Ano1)) - 20000.0 ForestDavis12_gamma((Org7Exit1P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org7Exit1P,Ano2))_:  1.0 ForestDavis12_f((Org7Exit1P,Ano2)) - 20480.0 ForestDavis12_gamma((Org7Exit1P,Ano1)) - 20480.0 ForestDavis12_gamma((Org7Exit1P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org2Exit1P,Ano1))_:  1.0 ForestDavis12_f((Org2Exit1P,Ano1)) - 19800.0 ForestDavis12_gamma((Org2Exit1P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org2Exit1P,Ano2))_:  1.0 ForestDavis12_f((Org2Exit1P,Ano2)) - 21480.0 ForestDavis12_gamma((Org2Exit1P,Ano1)) - 21480.0 ForestDavis12_gamma((Org2Exit1P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org1Int3P,Ano1))_:  1.0 ForestDavis12_f((Org1Int3P,Ano1)) - 18750.0 ForestDavis12_gamma((Org1Int3P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org1Int3P,Ano2))_:  1.0 ForestDavis12_f((Org1Int3P,Ano2)) - 19350.0 ForestDavis12_gamma((Org1Int3P,Ano1)) - 19350.0 ForestDavis12_gamma((Org1Int3P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Int1Exit1P,Ano1))_:  1.0 ForestDavis12_f((Int1Exit1P,Ano1)) - 17583.0 ForestDavis12_gamma((Int1Exit1P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Int1Exit1P,Ano2))_:  1.0 ForestDavis12_f((Int1Exit1P,Ano2)) - 19033.0 ForestDavis12_gamma((Int1Exit1P,Ano1)) - 19033.0 ForestDavis12_gamma((Int1Exit1P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org1Org3P,Ano1))_:  1.0 ForestDavis12_f((Org1Org3P,Ano1)) - 18750.0 ForestDavis12_gamma((Org1Org3P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org1Org3P,Ano2))_:  1.0 ForestDavis12_f((Org1Org3P,Ano2)) - 19350.0 ForestDavis12_gamma((Org1Org3P,Ano1)) - 19350.0 ForestDavis12_gamma((Org1Org3P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org4Org9P,Ano1))_:  1.0 ForestDavis12_f((Org4Org9P,Ano1)) - 18750.0 ForestDavis12_gamma((Org4Org9P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org4Org9P,Ano2))_:  1.0 ForestDavis12_f((Org4Org9P,Ano2)) - 20700.0 ForestDavis12_gamma((Org4Org9P,Ano1)) - 20700.0 ForestDavis12_gamma((Org4Org9P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Int1Org5P,Ano1))_:  1.0 ForestDavis12_f((Int1Org5P,Ano1)) - 17583.0 ForestDavis12_gamma((Int1Org5P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Int1Org5P,Ano2))_:  1.0 ForestDavis12_f((Int1Org5P,Ano2)) - 19033.0 ForestDavis12_gamma((Int1Org5P,Ano1)) - 19033.0 ForestDavis12_gamma((Int1Org5P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org8Exit1P,Ano1))_:  1.0 ForestDavis12_f((Org8Exit1P,Ano1)) - 18750.0 ForestDavis12_gamma((Org8Exit1P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org8Exit1P,Ano2))_:  1.0 ForestDavis12_f((Org8Exit1P,Ano2)) - 19350.0 ForestDavis12_gamma((Org8Exit1P,Ano1)) - 19350.0 ForestDavis12_gamma((Org8Exit1P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org9Int2P,Ano1))_:  1.0 ForestDavis12_f((Org9Int2P,Ano1)) - 19800.0 ForestDavis12_gamma((Org9Int2P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Org9Int2P,Ano2))_:  1.0 ForestDavis12_f((Org9Int2P,Ano2)) - 20400.0 ForestDavis12_gamma((Org9Int2P,Ano1)) - 20400.0 ForestDavis12_gamma((Org9Int2P,Ano2)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Int1Int3P,Ano1))_:  1.0 ForestDavis12_f((Int1Int3P,Ano1)) - 17583.0 ForestDavis12_gamma((Int1Int3P,Ano1)) <= 0.0

ForestDavis12_c_u_EnforcePotentialRoadFlowCap((Int1Int3P,Ano2))_:  1.0 ForestDavis12_f((Int1Int3P,Ano2)) - 19033.0 ForestDavis12_gamma((Int1Int3P,Ano1)) - 19033.0 ForestDavis12_gamma((Int1Int3P,Ano2)) <= 0.0

ForestDavis12_c_e_EnforceIntersectionFlowBalance((Intersection1,Ano1))_:  -1.0 ForestDavis12_f((Int1Exit1P,Ano1)) - 1.0 ForestDavis12_f((Int1Int2E,Ano1)) - 1.0 ForestDavis12_f((Int1Int3P,Ano1)) - 1.0 ForestDavis12_f((Int1Org5P,Ano1)) + 1.0 ForestDavis12_f((Org3Int1P,Ano1)) 
+ 1.0 ForestDavis12_f((Org4Int1P,Ano1)) = 0.0

ForestDavis12_c_e_EnforceIntersectionFlowBalance((Intersection1,Ano2))_:  -1.0 ForestDavis12_f((Int1Exit1P,Ano2)) - 1.0 ForestDavis12_f((Int1Int2E,Ano2)) - 1.0 ForestDavis12_f((Int1Int3P,Ano2)) - 1.0 ForestDavis12_f((Int1Org5P,Ano2)) + 1.0 ForestDavis12_f((Org3Int1P,Ano2)) 
+ 1.0 ForestDavis12_f((Org4Int1P,Ano2)) = 0.0

ForestDavis12_c_e_EnforceIntersectionFlowBalance((Intersection2,Ano1))_:  1.0 ForestDavis12_f((Int1Int2E,Ano1)) - 1.0 ForestDavis12_f((Int2Exit1E,Ano1)) + 1.0 ForestDavis12_f((Org7Int2E,Ano1)) + 1.0 ForestDavis12_f((Org9Int2P,Ano1)) = 0.0

ForestDavis12_c_e_EnforceIntersectionFlowBalance((Intersection2,Ano2))_:  1.0 ForestDavis12_f((Int1Int2E,Ano2)) - 1.0 ForestDavis12_f((Int2Exit1E,Ano2)) + 1.0 ForestDavis12_f((Org7Int2E,Ano2)) + 1.0 ForestDavis12_f((Org9Int2P,Ano2)) = 0.0

ForestDavis12_c_e_EnforceIntersectionFlowBalance((Intersection3,Ano1))_:  1.0 ForestDavis12_f((Int1Int3P,Ano1)) - 1.0 ForestDavis12_f((Int3Exit1E,Ano1)) + 1.0 ForestDavis12_f((Org1Int3P,Ano1)) + 1.0 ForestDavis12_f((Org2Int3E,Ano1)) = 0.0

ForestDavis12_c_e_EnforceIntersectionFlowBalance((Intersection3,Ano2))_:  1.0 ForestDavis12_f((Int1Int3P,Ano2)) - 1.0 ForestDavis12_f((Int3Exit1E,Ano2)) + 1.0 ForestDavis12_f((Org1Int3P,Ano2)) + 1.0 ForestDavis12_f((Org2Int3E,Ano2)) = 0.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Int3Exit1E,Ano1))_:  1.0 ForestDavis12_f((Int3Exit1E,Ano1)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Int3Exit1E,Ano1))_:  1.0 ForestDavis12_f((Int3Exit1E,Ano1)) <= 17583.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Int3Exit1E,Ano2))_:  1.0 ForestDavis12_f((Int3Exit1E,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Int3Exit1E,Ano2))_:  1.0 ForestDavis12_f((Int3Exit1E,Ano2)) <= 18720.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Int1Int2E,Ano1))_:  1.0 ForestDavis12_f((Int1Int2E,Ano1)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Int1Int2E,Ano1))_:  1.0 ForestDavis12_f((Int1Int2E,Ano1)) <= 15000.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Int1Int2E,Ano2))_:  1.0 ForestDavis12_f((Int1Int2E,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Int1Int2E,Ano2))_:  1.0 ForestDavis12_f((Int1Int2E,Ano2)) <= 15100.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Org2Int3E,Ano1))_:  1.0 ForestDavis12_f((Org2Int3E,Ano1)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Org2Int3E,Ano1))_:  1.0 ForestDavis12_f((Org2Int3E,Ano1)) <= 18000.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Org2Int3E,Ano2))_:  1.0 ForestDavis12_f((Org2Int3E,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Org2Int3E,Ano2))_:  1.0 ForestDavis12_f((Org2Int3E,Ano2)) <= 18720.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Org7Int2E,Ano1))_:  1.0 ForestDavis12_f((Org7Int2E,Ano1)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Org7Int2E,Ano1))_:  1.0 ForestDavis12_f((Org7Int2E,Ano1)) <= 18000.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Org7Int2E,Ano2))_:  1.0 ForestDavis12_f((Org7Int2E,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Org7Int2E,Ano2))_:  1.0 ForestDavis12_f((Org7Int2E,Ano2)) <= 18180.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Org5Exit1E,Ano1))_:  1.0 ForestDavis12_f((Org5Exit1E,Ano1)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Org5Exit1E,Ano1))_:  1.0 ForestDavis12_f((Org5Exit1E,Ano1)) <= 15000.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Org5Exit1E,Ano2))_:  1.0 ForestDavis12_f((Org5Exit1E,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Org5Exit1E,Ano2))_:  1.0 ForestDavis12_f((Org5Exit1E,Ano2)) <= 15700.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Int2Exit1E,Ano1))_:  1.0 ForestDavis12_f((Int2Exit1E,Ano1)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Int2Exit1E,Ano1))_:  1.0 ForestDavis12_f((Int2Exit1E,Ano1)) <= 15000.0

ForestDavis12_c_l_EnforceExistingRoadCapacities((Int2Exit1E,Ano2))_:  1.0 ForestDavis12_f((Int2Exit1E,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceExistingRoadCapacities((Int2Exit1E,Ano2))_:  1.0 ForestDavis12_f((Int2Exit1E,Ano2)) <= 15100.0

ForestDavis12_c_l_EnforceOneHarvest(TrackNine)_:  1.0 ForestDavis12_delta((TrackNine,Ano1)) + 1.0 ForestDavis12_delta((TrackNine,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackNine)_:  1.0 ForestDavis12_delta((TrackNine,Ano1)) + 1.0 ForestDavis12_delta((TrackNine,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackTwentyThree)_:  1.0 ForestDavis12_delta((TrackTwentyThree,Ano1)) + 1.0 ForestDavis12_delta((TrackTwentyThree,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackTwentyThree)_:  1.0 ForestDavis12_delta((TrackTwentyThree,Ano1)) + 1.0 ForestDavis12_delta((TrackTwentyThree,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackOne)_:  1.0 ForestDavis12_delta((TrackOne,Ano1)) + 1.0 ForestDavis12_delta((TrackOne,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackOne)_:  1.0 ForestDavis12_delta((TrackOne,Ano1)) + 1.0 ForestDavis12_delta((TrackOne,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackEleven)_:  1.0 ForestDavis12_delta((TrackEleven,Ano1)) + 1.0 ForestDavis12_delta((TrackEleven,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackEleven)_:  1.0 ForestDavis12_delta((TrackEleven,Ano1)) + 1.0 ForestDavis12_delta((TrackEleven,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackThree)_:  1.0 ForestDavis12_delta((TrackThree,Ano1)) + 1.0 ForestDavis12_delta((TrackThree,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackThree)_:  1.0 ForestDavis12_delta((TrackThree,Ano1)) + 1.0 ForestDavis12_delta((TrackThree,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackTwentyFour)_:  1.0 ForestDavis12_delta((TrackTwentyFour,Ano1)) + 1.0 ForestDavis12_delta((TrackTwentyFour,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackTwentyFour)_:  1.0 ForestDavis12_delta((TrackTwentyFour,Ano1)) + 1.0 ForestDavis12_delta((TrackTwentyFour,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackSeventeen)_:  1.0 ForestDavis12_delta((TrackSeventeen,Ano1)) + 1.0 ForestDavis12_delta((TrackSeventeen,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackSeventeen)_:  1.0 ForestDavis12_delta((TrackSeventeen,Ano1)) + 1.0 ForestDavis12_delta((TrackSeventeen,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackTwelve)_:  1.0 ForestDavis12_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis12_delta((TrackTwelve,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackTwelve)_:  1.0 ForestDavis12_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis12_delta((TrackTwelve,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackNineteen)_:  1.0 ForestDavis12_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis12_delta((TrackNineteen,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackNineteen)_:  1.0 ForestDavis12_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis12_delta((TrackNineteen,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackTen)_:  1.0 ForestDavis12_delta((TrackTen,Ano1)) + 1.0 ForestDavis12_delta((TrackTen,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackTen)_:  1.0 ForestDavis12_delta((TrackTen,Ano1)) + 1.0 ForestDavis12_delta((TrackTen,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackThirteen)_:  1.0 ForestDavis12_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis12_delta((TrackThirteen,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackThirteen)_:  1.0 ForestDavis12_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis12_delta((TrackThirteen,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackTwenty)_:  1.0 ForestDavis12_delta((TrackTwenty,Ano1)) + 1.0 ForestDavis12_delta((TrackTwenty,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackTwenty)_:  1.0 ForestDavis12_delta((TrackTwenty,Ano1)) + 1.0 ForestDavis12_delta((TrackTwenty,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackTwentyTwo)_:  1.0 ForestDavis12_delta((TrackTwentyTwo,Ano1)) + 1.0 ForestDavis12_delta((TrackTwentyTwo,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackTwentyTwo)_:  1.0 ForestDavis12_delta((TrackTwentyTwo,Ano1)) + 1.0 ForestDavis12_delta((TrackTwentyTwo,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackSixteen)_:  1.0 ForestDavis12_delta((TrackSixteen,Ano1)) + 1.0 ForestDavis12_delta((TrackSixteen,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackSixteen)_:  1.0 ForestDavis12_delta((TrackSixteen,Ano1)) + 1.0 ForestDavis12_delta((TrackSixteen,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackTwo)_:  1.0 ForestDavis12_delta((TrackTwo,Ano1)) + 1.0 ForestDavis12_delta((TrackTwo,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackTwo)_:  1.0 ForestDavis12_delta((TrackTwo,Ano1)) + 1.0 ForestDavis12_delta((TrackTwo,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackSix)_:  1.0 ForestDavis12_delta((TrackSix,Ano1)) + 1.0 ForestDavis12_delta((TrackSix,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackSix)_:  1.0 ForestDavis12_delta((TrackSix,Ano1)) + 1.0 ForestDavis12_delta((TrackSix,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackSeven)_:  1.0 ForestDavis12_delta((TrackSeven,Ano1)) + 1.0 ForestDavis12_delta((TrackSeven,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackSeven)_:  1.0 ForestDavis12_delta((TrackSeven,Ano1)) + 1.0 ForestDavis12_delta((TrackSeven,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackFifteen)_:  1.0 ForestDavis12_delta((TrackFifteen,Ano1)) + 1.0 ForestDavis12_delta((TrackFifteen,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackFifteen)_:  1.0 ForestDavis12_delta((TrackFifteen,Ano1)) + 1.0 ForestDavis12_delta((TrackFifteen,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackFour)_:  1.0 ForestDavis12_delta((TrackFour,Ano1)) + 1.0 ForestDavis12_delta((TrackFour,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackFour)_:  1.0 ForestDavis12_delta((TrackFour,Ano1)) + 1.0 ForestDavis12_delta((TrackFour,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackFourteen)_:  1.0 ForestDavis12_delta((TrackFourteen,Ano1)) + 1.0 ForestDavis12_delta((TrackFourteen,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackFourteen)_:  1.0 ForestDavis12_delta((TrackFourteen,Ano1)) + 1.0 ForestDavis12_delta((TrackFourteen,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackTwentyOne)_:  1.0 ForestDavis12_delta((TrackTwentyOne,Ano1)) + 1.0 ForestDavis12_delta((TrackTwentyOne,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackTwentyOne)_:  1.0 ForestDavis12_delta((TrackTwentyOne,Ano1)) + 1.0 ForestDavis12_delta((TrackTwentyOne,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackEighteen)_:  1.0 ForestDavis12_delta((TrackEighteen,Ano1)) + 1.0 ForestDavis12_delta((TrackEighteen,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackEighteen)_:  1.0 ForestDavis12_delta((TrackEighteen,Ano1)) + 1.0 ForestDavis12_delta((TrackEighteen,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackFive)_:  1.0 ForestDavis12_delta((TrackFive,Ano1)) + 1.0 ForestDavis12_delta((TrackFive,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackFive)_:  1.0 ForestDavis12_delta((TrackFive,Ano1)) + 1.0 ForestDavis12_delta((TrackFive,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackTwentyFive)_:  1.0 ForestDavis12_delta((TrackTwentyFive,Ano1)) + 1.0 ForestDavis12_delta((TrackTwentyFive,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackTwentyFive)_:  1.0 ForestDavis12_delta((TrackTwentyFive,Ano1)) + 1.0 ForestDavis12_delta((TrackTwentyFive,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOneHarvest(TrackEight)_:  1.0 ForestDavis12_delta((TrackEight,Ano1)) + 1.0 ForestDavis12_delta((TrackEight,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOneHarvest(TrackEight)_:  1.0 ForestDavis12_delta((TrackEight,Ano1)) + 1.0 ForestDavis12_delta((TrackEight,Ano2)) <= 1.0

ForestDavis12_c_e_ComputeStageProfit(Ano1)_:  1.0 ForestDavis12_AnoProfit(Ano1) + 711000.0 ForestDavis12_delta((TrackEight,Ano1)) + 447000.0 ForestDavis12_delta((TrackEighteen,Ano1)) + 507000.0 ForestDavis12_delta((TrackEleven,Ano1)) + 618750.0 ForestDavis12_delta((TrackFifteen,Ano1)) 
+ 560000.0 ForestDavis12_delta((TrackFive,Ano1)) + 375000.0 ForestDavis12_delta((TrackFour,Ano1)) + 387500.0 ForestDavis12_delta((TrackFourteen,Ano1)) + 453750.0 ForestDavis12_delta((TrackNine,Ano1)) + 275000.0 ForestDavis12_delta((TrackNineteen,Ano1)) 
+ 412500.0 ForestDavis12_delta((TrackOne,Ano1)) + 461250.0 ForestDavis12_delta((TrackSeven,Ano1)) + 535500.0 ForestDavis12_delta((TrackSeventeen,Ano1)) + 656250.0 ForestDavis12_delta((TrackSix,Ano1)) + 561000.0 ForestDavis12_delta((TrackSixteen,Ano1)) 
+ 656250.0 ForestDavis12_delta((TrackTen,Ano1)) + 386750.0 ForestDavis12_delta((TrackThirteen,Ano1)) + 375000.0 ForestDavis12_delta((TrackThree,Ano1)) + 630000.0 ForestDavis12_delta((TrackTwelve,Ano1)) + 326250.0 ForestDavis12_delta((TrackTwenty,Ano1)) 
+ 393750.0 ForestDavis12_delta((TrackTwentyFive,Ano1)) + 330000.0 ForestDavis12_delta((TrackTwentyFour,Ano1)) + 468750.0 ForestDavis12_delta((TrackTwentyOne,Ano1)) + 315000.0 ForestDavis12_delta((TrackTwentyThree,Ano1)) + 431250.0 ForestDavis12_delta((TrackTwentyTwo,Ano1)) 
+ 400000.0 ForestDavis12_delta((TrackTwo,Ano1)) + 20.0 ForestDavis12_f((Int1Exit1P,Ano1)) + 17.0 ForestDavis12_f((Int1Int2E,Ano1)) + 14.0 ForestDavis12_f((Int1Int3P,Ano1)) + 10.0 ForestDavis12_f((Int1Org5P,Ano1)) 
+ 8.0 ForestDavis12_f((Int2Exit1E,Ano1)) + 15.0 ForestDavis12_f((Int3Exit1E,Ano1)) + 10.0 ForestDavis12_f((Org1Int3P,Ano1)) + 5.0 ForestDavis12_f((Org1Org2P,Ano1)) + 14.0 ForestDavis12_f((Org1Org3P,Ano1)) 
+ 21.0 ForestDavis12_f((Org2Exit1P,Ano1)) + 5.0 ForestDavis12_f((Org2Int3E,Ano1)) + 5.0 ForestDavis12_f((Org3Int1P,Ano1)) + 8.0 ForestDavis12_f((Org4Int1P,Ano1)) + 15.0 ForestDavis12_f((Org4Org9P,Ano1)) 
+ 12.0 ForestDavis12_f((Org5Exit1E,Ano1)) + 12.0 ForestDavis12_f((Org6Exit1P,Ano1)) + 15.0 ForestDavis12_f((Org7Exit1P,Ano1)) + 8.0 ForestDavis12_f((Org7Int2E,Ano1)) + 5.0 ForestDavis12_f((Org8Exit1P,Ano1)) 
+ 8.0 ForestDavis12_f((Org9Int2P,Ano1)) + 1800.0 ForestDavis12_gamma((Int1Exit1P,Ano1)) + 1750.0 ForestDavis12_gamma((Int1Int3P,Ano1)) + 1050.0 ForestDavis12_gamma((Int1Org5P,Ano1)) + 1110.0 ForestDavis12_gamma((Org1Int3P,Ano1)) 
+ 900.0 ForestDavis12_gamma((Org1Org2P,Ano1)) + 1200.0 ForestDavis12_gamma((Org1Org3P,Ano1)) + 2840.0 ForestDavis12_gamma((Org2Exit1P,Ano1)) + 900.0 ForestDavis12_gamma((Org3Int1P,Ano1)) + 1050.0 ForestDavis12_gamma((Org4Int1P,Ano1)) 
+ 1750.0 ForestDavis12_gamma((Org4Org9P,Ano1)) + 1550.0 ForestDavis12_gamma((Org6Exit1P,Ano1)) + 1750.0 ForestDavis12_gamma((Org7Exit1P,Ano1)) + 990.0 ForestDavis12_gamma((Org8Exit1P,Ano1)) + 1200.0 ForestDavis12_gamma((Org9Int2P,Ano1)) 
- 45.0 ForestDavis12_z((Exit1,Ano1)) = 0.0

ForestDavis12_c_e_ComputeStageProfit(Ano2)_:  1.0 ForestDavis12_AnoProfit(Ano2) + 673560.0 ForestDavis12_delta((TrackEight,Ano2)) + 442320.0 ForestDavis12_delta((TrackEighteen,Ano2)) + 513120.0 ForestDavis12_delta((TrackEleven,Ano2)) + 590250.0 ForestDavis12_delta((TrackFifteen,Ano2)) 
+ 562380.0 ForestDavis12_delta((TrackFive,Ano2)) + 362900.0 ForestDavis12_delta((TrackFour,Ano2)) + 383200.0 ForestDavis12_delta((TrackFourteen,Ano2)) + 441650.0 ForestDavis12_delta((TrackNine,Ano2)) + 291500.0 ForestDavis12_delta((TrackNineteen,Ano2)) 
+ 418990.0 ForestDavis12_delta((TrackOne,Ano2)) + 454680.0 ForestDavis12_delta((TrackSeven,Ano2)) + 529620.0 ForestDavis12_delta((TrackSeventeen,Ano2)) + 631200.0 ForestDavis12_delta((TrackSix,Ano2)) + 538800.0 ForestDavis12_delta((TrackSixteen,Ano2)) 
+ 651450.0 ForestDavis12_delta((TrackTen,Ano2)) + 389270.0 ForestDavis12_delta((TrackThirteen,Ano2)) + 374900.0 ForestDavis12_delta((TrackThree,Ano2)) + 608040.0 ForestDavis12_delta((TrackTwelve,Ano2)) + 323820.0 ForestDavis12_delta((TrackTwenty,Ano2)) 
+ 392550.0 ForestDavis12_delta((TrackTwentyFive,Ano2)) + 334480.0 ForestDavis12_delta((TrackTwentyFour,Ano2)) + 476400.0 ForestDavis12_delta((TrackTwentyOne,Ano2)) + 310950.0 ForestDavis12_delta((TrackTwentyThree,Ano2)) + 426600.0 ForestDavis12_delta((TrackTwentyTwo,Ano2)) 
+ 405100.0 ForestDavis12_delta((TrackTwo,Ano2)) + 20.0 ForestDavis12_f((Int1Exit1P,Ano2)) + 17.0 ForestDavis12_f((Int1Int2E,Ano2)) + 14.0 ForestDavis12_f((Int1Int3P,Ano2)) + 10.0 ForestDavis12_f((Int1Org5P,Ano2)) 
+ 8.0 ForestDavis12_f((Int2Exit1E,Ano2)) + 15.0 ForestDavis12_f((Int3Exit1E,Ano2)) + 10.0 ForestDavis12_f((Org1Int3P,Ano2)) + 5.0 ForestDavis12_f((Org1Org2P,Ano2)) + 14.0 ForestDavis12_f((Org1Org3P,Ano2)) 
+ 21.0 ForestDavis12_f((Org2Exit1P,Ano2)) + 5.0 ForestDavis12_f((Org2Int3E,Ano2)) + 5.0 ForestDavis12_f((Org3Int1P,Ano2)) + 8.0 ForestDavis12_f((Org4Int1P,Ano2)) + 15.0 ForestDavis12_f((Org4Org9P,Ano2)) 
+ 12.0 ForestDavis12_f((Org5Exit1E,Ano2)) + 12.0 ForestDavis12_f((Org6Exit1P,Ano2)) + 15.0 ForestDavis12_f((Org7Exit1P,Ano2)) + 8.0 ForestDavis12_f((Org7Int2E,Ano2)) + 5.0 ForestDavis12_f((Org8Exit1P,Ano2)) 
+ 8.0 ForestDavis12_f((Org9Int2P,Ano2)) + 1636.0 ForestDavis12_gamma((Int1Exit1P,Ano2)) + 1591.0 ForestDavis12_gamma((Int1Int3P,Ano2)) + 955.0 ForestDavis12_gamma((Int1Org5P,Ano2)) + 1009.0 ForestDavis12_gamma((Org1Int3P,Ano2)) 
+ 818.0 ForestDavis12_gamma((Org1Org2P,Ano2)) + 1091.0 ForestDavis12_gamma((Org1Org3P,Ano2)) + 2582.0 ForestDavis12_gamma((Org2Exit1P,Ano2)) + 818.0 ForestDavis12_gamma((Org3Int1P,Ano2)) + 955.0 ForestDavis12_gamma((Org4Int1P,Ano2)) 
+ 1591.0 ForestDavis12_gamma((Org4Org9P,Ano2)) + 1409.0 ForestDavis12_gamma((Org6Exit1P,Ano2)) + 1591.0 ForestDavis12_gamma((Org7Exit1P,Ano2)) + 900.0 ForestDavis12_gamma((Org8Exit1P,Ano2)) + 1091.0 ForestDavis12_gamma((Org9Int2P,Ano2)) 
- 45.0 ForestDavis12_z((Exit1,Ano2)) = 0.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org1Org2P)_:  1.0 ForestDavis12_gamma((Org1Org2P,Ano1)) + 1.0 ForestDavis12_gamma((Org1Org2P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org1Org2P)_:  1.0 ForestDavis12_gamma((Org1Org2P,Ano1)) + 1.0 ForestDavis12_gamma((Org1Org2P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org6Exit1P)_:  1.0 ForestDavis12_gamma((Org6Exit1P,Ano1)) + 1.0 ForestDavis12_gamma((Org6Exit1P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org6Exit1P)_:  1.0 ForestDavis12_gamma((Org6Exit1P,Ano1)) + 1.0 ForestDavis12_gamma((Org6Exit1P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org3Int1P)_:  1.0 ForestDavis12_gamma((Org3Int1P,Ano1)) + 1.0 ForestDavis12_gamma((Org3Int1P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org3Int1P)_:  1.0 ForestDavis12_gamma((Org3Int1P,Ano1)) + 1.0 ForestDavis12_gamma((Org3Int1P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org4Int1P)_:  1.0 ForestDavis12_gamma((Org4Int1P,Ano1)) + 1.0 ForestDavis12_gamma((Org4Int1P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org4Int1P)_:  1.0 ForestDavis12_gamma((Org4Int1P,Ano1)) + 1.0 ForestDavis12_gamma((Org4Int1P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org7Exit1P)_:  1.0 ForestDavis12_gamma((Org7Exit1P,Ano1)) + 1.0 ForestDavis12_gamma((Org7Exit1P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org7Exit1P)_:  1.0 ForestDavis12_gamma((Org7Exit1P,Ano1)) + 1.0 ForestDavis12_gamma((Org7Exit1P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org2Exit1P)_:  1.0 ForestDavis12_gamma((Org2Exit1P,Ano1)) + 1.0 ForestDavis12_gamma((Org2Exit1P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org2Exit1P)_:  1.0 ForestDavis12_gamma((Org2Exit1P,Ano1)) + 1.0 ForestDavis12_gamma((Org2Exit1P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org1Int3P)_:  1.0 ForestDavis12_gamma((Org1Int3P,Ano1)) + 1.0 ForestDavis12_gamma((Org1Int3P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org1Int3P)_:  1.0 ForestDavis12_gamma((Org1Int3P,Ano1)) + 1.0 ForestDavis12_gamma((Org1Int3P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Int1Exit1P)_:  1.0 ForestDavis12_gamma((Int1Exit1P,Ano1)) + 1.0 ForestDavis12_gamma((Int1Exit1P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Int1Exit1P)_:  1.0 ForestDavis12_gamma((Int1Exit1P,Ano1)) + 1.0 ForestDavis12_gamma((Int1Exit1P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org1Org3P)_:  1.0 ForestDavis12_gamma((Org1Org3P,Ano1)) + 1.0 ForestDavis12_gamma((Org1Org3P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org1Org3P)_:  1.0 ForestDavis12_gamma((Org1Org3P,Ano1)) + 1.0 ForestDavis12_gamma((Org1Org3P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org4Org9P)_:  1.0 ForestDavis12_gamma((Org4Org9P,Ano1)) + 1.0 ForestDavis12_gamma((Org4Org9P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org4Org9P)_:  1.0 ForestDavis12_gamma((Org4Org9P,Ano1)) + 1.0 ForestDavis12_gamma((Org4Org9P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Int1Org5P)_:  1.0 ForestDavis12_gamma((Int1Org5P,Ano1)) + 1.0 ForestDavis12_gamma((Int1Org5P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Int1Org5P)_:  1.0 ForestDavis12_gamma((Int1Org5P,Ano1)) + 1.0 ForestDavis12_gamma((Int1Org5P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org8Exit1P)_:  1.0 ForestDavis12_gamma((Org8Exit1P,Ano1)) + 1.0 ForestDavis12_gamma((Org8Exit1P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org8Exit1P)_:  1.0 ForestDavis12_gamma((Org8Exit1P,Ano1)) + 1.0 ForestDavis12_gamma((Org8Exit1P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Org9Int2P)_:  1.0 ForestDavis12_gamma((Org9Int2P,Ano1)) + 1.0 ForestDavis12_gamma((Org9Int2P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Org9Int2P)_:  1.0 ForestDavis12_gamma((Org9Int2P,Ano1)) + 1.0 ForestDavis12_gamma((Org9Int2P,Ano2)) <= 1.0

ForestDavis12_c_l_EnforceOnePotentialRoad(Int1Int3P)_:  1.0 ForestDavis12_gamma((Int1Int3P,Ano1)) + 1.0 ForestDavis12_gamma((Int1Int3P,Ano2)) >= 0.0

ForestDavis12_c_u_EnforceOnePotentialRoad(Int1Int3P)_:  1.0 ForestDavis12_gamma((Int1Int3P,Ano1)) + 1.0 ForestDavis12_gamma((Int1Int3P,Ano2)) <= 1.0

c_e_ONE_VAR_CONSTANT: ONE_VAR_CONSTANT = 1.0

\ End constraint block for scenario ForestDavis12

\ Begin constraint block for scenario ForestDavis4
ForestDavis4_c_e_EnforceOriginFlowBalance((Origin5,Ano1))_:  15000.0 ForestDavis4_delta((TrackFourteen,Ano1)) + 17500.0 ForestDavis4_delta((TrackSeventeen,Ano1)) + 19950.0 ForestDavis4_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis4_f((Int1Org5P,Ano1)) - 1.0 ForestDavis4_f((Org5Exit1E,Ano1)) 
= 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin5,Ano2))_:  15700.0 ForestDavis4_delta((TrackFourteen,Ano2)) + 18760.0 ForestDavis4_delta((TrackSeventeen,Ano2)) + 20650.0 ForestDavis4_delta((TrackThirteen,Ano2)) + 1.0 ForestDavis4_f((Int1Org5P,Ano2)) - 1.0 ForestDavis4_f((Org5Exit1E,Ano2)) 
= 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin4,Ano1))_:  17500.0 ForestDavis4_delta((TrackFive,Ano1)) + 16500.0 ForestDavis4_delta((TrackNine,Ano1)) + 18750.0 ForestDavis4_delta((TrackTen,Ano1)) - 1.0 ForestDavis4_f((Org4Int1P,Ano1)) - 1.0 ForestDavis4_f((Org4Org9P,Ano1)) 
= 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin4,Ano2))_:  19460.0 ForestDavis4_delta((TrackFive,Ano2)) + 16940.0 ForestDavis4_delta((TrackNine,Ano2)) + 20700.0 ForestDavis4_delta((TrackTen,Ano2)) - 1.0 ForestDavis4_f((Org4Int1P,Ano2)) - 1.0 ForestDavis4_f((Org4Org9P,Ano2)) 
= 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin7,Ano1))_:  18000.0 ForestDavis4_delta((TrackTwenty,Ano1)) + 18750.0 ForestDavis4_delta((TrackTwentyFive,Ano1)) + 20000.0 ForestDavis4_delta((TrackTwentyFour,Ano1)) - 1.0 ForestDavis4_f((Org7Exit1P,Ano1)) - 1.0 ForestDavis4_f((Org7Int2E,Ano1)) 
= 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin7,Ano2))_:  18180.0 ForestDavis4_delta((TrackTwenty,Ano2)) + 19350.0 ForestDavis4_delta((TrackTwentyFive,Ano2)) + 20480.0 ForestDavis4_delta((TrackTwentyFour,Ano2)) - 1.0 ForestDavis4_f((Org7Exit1P,Ano2)) - 1.0 ForestDavis4_f((Org7Int2E,Ano2)) 
= 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin6,Ano1))_:  19800.0 ForestDavis4_delta((TrackSixteen,Ano1)) + 18750.0 ForestDavis4_delta((TrackTwentyOne,Ano1)) - 1.0 ForestDavis4_f((Org6Exit1P,Ano1)) = 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin6,Ano2))_:  19920.0 ForestDavis4_delta((TrackSixteen,Ano2)) + 20400.0 ForestDavis4_delta((TrackTwentyOne,Ano2)) - 1.0 ForestDavis4_f((Org6Exit1P,Ano2)) = 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin1,Ano1))_:  16500.0 ForestDavis4_delta((TrackOne,Ano1)) + 18750.0 ForestDavis4_delta((TrackSix,Ano1)) + 15000.0 ForestDavis4_delta((TrackTwo,Ano1)) - 1.0 ForestDavis4_f((Org1Int3P,Ano1)) - 1.0 ForestDavis4_f((Org1Org2P,Ano1)) 
- 1.0 ForestDavis4_f((Org1Org3P,Ano1)) = 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin1,Ano2))_:  17930.0 ForestDavis4_delta((TrackOne,Ano2)) + 19350.0 ForestDavis4_delta((TrackSix,Ano2)) + 16400.0 ForestDavis4_delta((TrackTwo,Ano2)) - 1.0 ForestDavis4_f((Org1Int3P,Ano2)) - 1.0 ForestDavis4_f((Org1Org2P,Ano2)) 
- 1.0 ForestDavis4_f((Org1Org3P,Ano2)) = 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin3,Ano1))_:  18000.0 ForestDavis4_delta((TrackEight,Ano1)) + 15000.0 ForestDavis4_delta((TrackFour,Ano1)) + 15000.0 ForestDavis4_delta((TrackThree,Ano1)) + 1.0 ForestDavis4_f((Org1Org3P,Ano1)) - 1.0 ForestDavis4_f((Org3Int1P,Ano1)) 
= 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin3,Ano2))_:  18180.0 ForestDavis4_delta((TrackEight,Ano2)) + 15100.0 ForestDavis4_delta((TrackFour,Ano2)) + 15900.0 ForestDavis4_delta((TrackThree,Ano2)) + 1.0 ForestDavis4_f((Org1Org3P,Ano2)) - 1.0 ForestDavis4_f((Org3Int1P,Ano2)) 
= 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin2,Ano1))_:  19800.0 ForestDavis4_delta((TrackEleven,Ano1)) + 18000.0 ForestDavis4_delta((TrackSeven,Ano1)) + 18000.0 ForestDavis4_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis4_f((Org1Org2P,Ano1)) - 1.0 ForestDavis4_f((Org2Exit1P,Ano1)) 
- 1.0 ForestDavis4_f((Org2Int3E,Ano1)) = 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin2,Ano2))_:  21480.0 ForestDavis4_delta((TrackEleven,Ano2)) + 18720.0 ForestDavis4_delta((TrackSeven,Ano2)) + 18720.0 ForestDavis4_delta((TrackTwelve,Ano2)) + 1.0 ForestDavis4_f((Org1Org2P,Ano2)) - 1.0 ForestDavis4_f((Org2Exit1P,Ano2)) 
- 1.0 ForestDavis4_f((Org2Int3E,Ano2)) = 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin9,Ano1))_:  19800.0 ForestDavis4_delta((TrackEighteen,Ano1)) + 18750.0 ForestDavis4_delta((TrackFifteen,Ano1)) + 15000.0 ForestDavis4_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis4_f((Org4Org9P,Ano1)) - 1.0 ForestDavis4_f((Org9Int2P,Ano1)) 
= 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin9,Ano2))_:  20400.0 ForestDavis4_delta((TrackEighteen,Ano2)) + 18900.0 ForestDavis4_delta((TrackFifteen,Ano2)) + 16400.0 ForestDavis4_delta((TrackNineteen,Ano2)) + 1.0 ForestDavis4_f((Org4Org9P,Ano2)) - 1.0 ForestDavis4_f((Org9Int2P,Ano2)) 
= 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin8,Ano1))_:  18000.0 ForestDavis4_delta((TrackTwentyThree,Ano1)) + 18750.0 ForestDavis4_delta((TrackTwentyTwo,Ano1)) - 1.0 ForestDavis4_f((Org8Exit1P,Ano1)) = 0.0

ForestDavis4_c_e_EnforceOriginFlowBalance((Origin8,Ano2))_:  18000.0 ForestDavis4_delta((TrackTwentyThree,Ano2)) + 19350.0 ForestDavis4_delta((TrackTwentyTwo,Ano2)) - 1.0 ForestDavis4_f((Org8Exit1P,Ano2)) = 0.0

ForestDavis4_c_l_EnforceWoodProductionBounds(Ano1)_:  1.0 ForestDavis4_z((Exit1,Ano1)) >= 30000.0

ForestDavis4_c_u_EnforceWoodProductionBounds(Ano1)_:  1.0 ForestDavis4_z((Exit1,Ano1)) <= 40000.0

ForestDavis4_c_l_EnforceWoodProductionBounds(Ano2)_:  1.0 ForestDavis4_z((Exit1,Ano2)) >= 27000.0

ForestDavis4_c_u_EnforceWoodProductionBounds(Ano2)_:  1.0 ForestDavis4_z((Exit1,Ano2)) <= 50000.0

ForestDavis4_c_e_EnforceDestinationFlowBalance((Exit1,Ano1))_:  -1.0 ForestDavis4_f((Int1Exit1P,Ano1)) - 1.0 ForestDavis4_f((Int2Exit1E,Ano1)) - 1.0 ForestDavis4_f((Int3Exit1E,Ano1)) - 1.0 ForestDavis4_f((Org2Exit1P,Ano1)) - 1.0 ForestDavis4_f((Org5Exit1E,Ano1)) 
- 1.0 ForestDavis4_f((Org6Exit1P,Ano1)) - 1.0 ForestDavis4_f((Org7Exit1P,Ano1)) - 1.0 ForestDavis4_f((Org8Exit1P,Ano1)) + 1.0 ForestDavis4_z((Exit1,Ano1)) = 0.0

ForestDavis4_c_e_EnforceDestinationFlowBalance((Exit1,Ano2))_:  -1.0 ForestDavis4_f((Int1Exit1P,Ano2)) - 1.0 ForestDavis4_f((Int2Exit1E,Ano2)) - 1.0 ForestDavis4_f((Int3Exit1E,Ano2)) - 1.0 ForestDavis4_f((Org2Exit1P,Ano2)) - 1.0 ForestDavis4_f((Org5Exit1E,Ano2)) 
- 1.0 ForestDavis4_f((Org6Exit1P,Ano2)) - 1.0 ForestDavis4_f((Org7Exit1P,Ano2)) - 1.0 ForestDavis4_f((Org8Exit1P,Ano2)) + 1.0 ForestDavis4_z((Exit1,Ano2)) = 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org1Org2P,Ano1))_:  1.0 ForestDavis4_f((Org1Org2P,Ano1)) - 15000.0 ForestDavis4_gamma((Org1Org2P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org1Org2P,Ano2))_:  1.0 ForestDavis4_f((Org1Org2P,Ano2)) - 16400.0 ForestDavis4_gamma((Org1Org2P,Ano1)) - 16400.0 ForestDavis4_gamma((Org1Org2P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org6Exit1P,Ano1))_:  1.0 ForestDavis4_f((Org6Exit1P,Ano1)) - 19800.0 ForestDavis4_gamma((Org6Exit1P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org6Exit1P,Ano2))_:  1.0 ForestDavis4_f((Org6Exit1P,Ano2)) - 20400.0 ForestDavis4_gamma((Org6Exit1P,Ano1)) - 20400.0 ForestDavis4_gamma((Org6Exit1P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org3Int1P,Ano1))_:  1.0 ForestDavis4_f((Org3Int1P,Ano1)) - 15000.0 ForestDavis4_gamma((Org3Int1P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org3Int1P,Ano2))_:  1.0 ForestDavis4_f((Org3Int1P,Ano2)) - 15100.0 ForestDavis4_gamma((Org3Int1P,Ano1)) - 15100.0 ForestDavis4_gamma((Org3Int1P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org4Int1P,Ano1))_:  1.0 ForestDavis4_f((Org4Int1P,Ano1)) - 17583.0 ForestDavis4_gamma((Org4Int1P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org4Int1P,Ano2))_:  1.0 ForestDavis4_f((Org4Int1P,Ano2)) - 19033.0 ForestDavis4_gamma((Org4Int1P,Ano1)) - 19033.0 ForestDavis4_gamma((Org4Int1P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org7Exit1P,Ano1))_:  1.0 ForestDavis4_f((Org7Exit1P,Ano1)) - 20000.0 ForestDavis4_gamma((Org7Exit1P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org7Exit1P,Ano2))_:  1.0 ForestDavis4_f((Org7Exit1P,Ano2)) - 20480.0 ForestDavis4_gamma((Org7Exit1P,Ano1)) - 20480.0 ForestDavis4_gamma((Org7Exit1P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org2Exit1P,Ano1))_:  1.0 ForestDavis4_f((Org2Exit1P,Ano1)) - 19800.0 ForestDavis4_gamma((Org2Exit1P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org2Exit1P,Ano2))_:  1.0 ForestDavis4_f((Org2Exit1P,Ano2)) - 21480.0 ForestDavis4_gamma((Org2Exit1P,Ano1)) - 21480.0 ForestDavis4_gamma((Org2Exit1P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org1Int3P,Ano1))_:  1.0 ForestDavis4_f((Org1Int3P,Ano1)) - 18750.0 ForestDavis4_gamma((Org1Int3P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org1Int3P,Ano2))_:  1.0 ForestDavis4_f((Org1Int3P,Ano2)) - 19350.0 ForestDavis4_gamma((Org1Int3P,Ano1)) - 19350.0 ForestDavis4_gamma((Org1Int3P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Int1Exit1P,Ano1))_:  1.0 ForestDavis4_f((Int1Exit1P,Ano1)) - 17583.0 ForestDavis4_gamma((Int1Exit1P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Int1Exit1P,Ano2))_:  1.0 ForestDavis4_f((Int1Exit1P,Ano2)) - 19033.0 ForestDavis4_gamma((Int1Exit1P,Ano1)) - 19033.0 ForestDavis4_gamma((Int1Exit1P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org1Org3P,Ano1))_:  1.0 ForestDavis4_f((Org1Org3P,Ano1)) - 18750.0 ForestDavis4_gamma((Org1Org3P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org1Org3P,Ano2))_:  1.0 ForestDavis4_f((Org1Org3P,Ano2)) - 19350.0 ForestDavis4_gamma((Org1Org3P,Ano1)) - 19350.0 ForestDavis4_gamma((Org1Org3P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org4Org9P,Ano1))_:  1.0 ForestDavis4_f((Org4Org9P,Ano1)) - 18750.0 ForestDavis4_gamma((Org4Org9P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org4Org9P,Ano2))_:  1.0 ForestDavis4_f((Org4Org9P,Ano2)) - 20700.0 ForestDavis4_gamma((Org4Org9P,Ano1)) - 20700.0 ForestDavis4_gamma((Org4Org9P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Int1Org5P,Ano1))_:  1.0 ForestDavis4_f((Int1Org5P,Ano1)) - 17583.0 ForestDavis4_gamma((Int1Org5P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Int1Org5P,Ano2))_:  1.0 ForestDavis4_f((Int1Org5P,Ano2)) - 19033.0 ForestDavis4_gamma((Int1Org5P,Ano1)) - 19033.0 ForestDavis4_gamma((Int1Org5P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org8Exit1P,Ano1))_:  1.0 ForestDavis4_f((Org8Exit1P,Ano1)) - 18750.0 ForestDavis4_gamma((Org8Exit1P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org8Exit1P,Ano2))_:  1.0 ForestDavis4_f((Org8Exit1P,Ano2)) - 19350.0 ForestDavis4_gamma((Org8Exit1P,Ano1)) - 19350.0 ForestDavis4_gamma((Org8Exit1P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org9Int2P,Ano1))_:  1.0 ForestDavis4_f((Org9Int2P,Ano1)) - 19800.0 ForestDavis4_gamma((Org9Int2P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Org9Int2P,Ano2))_:  1.0 ForestDavis4_f((Org9Int2P,Ano2)) - 20400.0 ForestDavis4_gamma((Org9Int2P,Ano1)) - 20400.0 ForestDavis4_gamma((Org9Int2P,Ano2)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Int1Int3P,Ano1))_:  1.0 ForestDavis4_f((Int1Int3P,Ano1)) - 17583.0 ForestDavis4_gamma((Int1Int3P,Ano1)) <= 0.0

ForestDavis4_c_u_EnforcePotentialRoadFlowCap((Int1Int3P,Ano2))_:  1.0 ForestDavis4_f((Int1Int3P,Ano2)) - 19033.0 ForestDavis4_gamma((Int1Int3P,Ano1)) - 19033.0 ForestDavis4_gamma((Int1Int3P,Ano2)) <= 0.0

ForestDavis4_c_e_EnforceIntersectionFlowBalance((Intersection1,Ano1))_:  -1.0 ForestDavis4_f((Int1Exit1P,Ano1)) - 1.0 ForestDavis4_f((Int1Int2E,Ano1)) - 1.0 ForestDavis4_f((Int1Int3P,Ano1)) - 1.0 ForestDavis4_f((Int1Org5P,Ano1)) + 1.0 ForestDavis4_f((Org3Int1P,Ano1)) 
+ 1.0 ForestDavis4_f((Org4Int1P,Ano1)) = 0.0

ForestDavis4_c_e_EnforceIntersectionFlowBalance((Intersection1,Ano2))_:  -1.0 ForestDavis4_f((Int1Exit1P,Ano2)) - 1.0 ForestDavis4_f((Int1Int2E,Ano2)) - 1.0 ForestDavis4_f((Int1Int3P,Ano2)) - 1.0 ForestDavis4_f((Int1Org5P,Ano2)) + 1.0 ForestDavis4_f((Org3Int1P,Ano2)) 
+ 1.0 ForestDavis4_f((Org4Int1P,Ano2)) = 0.0

ForestDavis4_c_e_EnforceIntersectionFlowBalance((Intersection2,Ano1))_:  1.0 ForestDavis4_f((Int1Int2E,Ano1)) - 1.0 ForestDavis4_f((Int2Exit1E,Ano1)) + 1.0 ForestDavis4_f((Org7Int2E,Ano1)) + 1.0 ForestDavis4_f((Org9Int2P,Ano1)) = 0.0

ForestDavis4_c_e_EnforceIntersectionFlowBalance((Intersection2,Ano2))_:  1.0 ForestDavis4_f((Int1Int2E,Ano2)) - 1.0 ForestDavis4_f((Int2Exit1E,Ano2)) + 1.0 ForestDavis4_f((Org7Int2E,Ano2)) + 1.0 ForestDavis4_f((Org9Int2P,Ano2)) = 0.0

ForestDavis4_c_e_EnforceIntersectionFlowBalance((Intersection3,Ano1))_:  1.0 ForestDavis4_f((Int1Int3P,Ano1)) - 1.0 ForestDavis4_f((Int3Exit1E,Ano1)) + 1.0 ForestDavis4_f((Org1Int3P,Ano1)) + 1.0 ForestDavis4_f((Org2Int3E,Ano1)) = 0.0

ForestDavis4_c_e_EnforceIntersectionFlowBalance((Intersection3,Ano2))_:  1.0 ForestDavis4_f((Int1Int3P,Ano2)) - 1.0 ForestDavis4_f((Int3Exit1E,Ano2)) + 1.0 ForestDavis4_f((Org1Int3P,Ano2)) + 1.0 ForestDavis4_f((Org2Int3E,Ano2)) = 0.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Int3Exit1E,Ano1))_:  1.0 ForestDavis4_f((Int3Exit1E,Ano1)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Int3Exit1E,Ano1))_:  1.0 ForestDavis4_f((Int3Exit1E,Ano1)) <= 17583.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Int3Exit1E,Ano2))_:  1.0 ForestDavis4_f((Int3Exit1E,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Int3Exit1E,Ano2))_:  1.0 ForestDavis4_f((Int3Exit1E,Ano2)) <= 18720.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Int1Int2E,Ano1))_:  1.0 ForestDavis4_f((Int1Int2E,Ano1)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Int1Int2E,Ano1))_:  1.0 ForestDavis4_f((Int1Int2E,Ano1)) <= 15000.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Int1Int2E,Ano2))_:  1.0 ForestDavis4_f((Int1Int2E,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Int1Int2E,Ano2))_:  1.0 ForestDavis4_f((Int1Int2E,Ano2)) <= 15100.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Org2Int3E,Ano1))_:  1.0 ForestDavis4_f((Org2Int3E,Ano1)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Org2Int3E,Ano1))_:  1.0 ForestDavis4_f((Org2Int3E,Ano1)) <= 18000.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Org2Int3E,Ano2))_:  1.0 ForestDavis4_f((Org2Int3E,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Org2Int3E,Ano2))_:  1.0 ForestDavis4_f((Org2Int3E,Ano2)) <= 18720.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Org7Int2E,Ano1))_:  1.0 ForestDavis4_f((Org7Int2E,Ano1)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Org7Int2E,Ano1))_:  1.0 ForestDavis4_f((Org7Int2E,Ano1)) <= 18000.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Org7Int2E,Ano2))_:  1.0 ForestDavis4_f((Org7Int2E,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Org7Int2E,Ano2))_:  1.0 ForestDavis4_f((Org7Int2E,Ano2)) <= 18180.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Org5Exit1E,Ano1))_:  1.0 ForestDavis4_f((Org5Exit1E,Ano1)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Org5Exit1E,Ano1))_:  1.0 ForestDavis4_f((Org5Exit1E,Ano1)) <= 15000.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Org5Exit1E,Ano2))_:  1.0 ForestDavis4_f((Org5Exit1E,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Org5Exit1E,Ano2))_:  1.0 ForestDavis4_f((Org5Exit1E,Ano2)) <= 15700.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Int2Exit1E,Ano1))_:  1.0 ForestDavis4_f((Int2Exit1E,Ano1)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Int2Exit1E,Ano1))_:  1.0 ForestDavis4_f((Int2Exit1E,Ano1)) <= 15000.0

ForestDavis4_c_l_EnforceExistingRoadCapacities((Int2Exit1E,Ano2))_:  1.0 ForestDavis4_f((Int2Exit1E,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceExistingRoadCapacities((Int2Exit1E,Ano2))_:  1.0 ForestDavis4_f((Int2Exit1E,Ano2)) <= 15100.0

ForestDavis4_c_l_EnforceOneHarvest(TrackNine)_:  1.0 ForestDavis4_delta((TrackNine,Ano1)) + 1.0 ForestDavis4_delta((TrackNine,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackNine)_:  1.0 ForestDavis4_delta((TrackNine,Ano1)) + 1.0 ForestDavis4_delta((TrackNine,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackTwentyThree)_:  1.0 ForestDavis4_delta((TrackTwentyThree,Ano1)) + 1.0 ForestDavis4_delta((TrackTwentyThree,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackTwentyThree)_:  1.0 ForestDavis4_delta((TrackTwentyThree,Ano1)) + 1.0 ForestDavis4_delta((TrackTwentyThree,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackOne)_:  1.0 ForestDavis4_delta((TrackOne,Ano1)) + 1.0 ForestDavis4_delta((TrackOne,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackOne)_:  1.0 ForestDavis4_delta((TrackOne,Ano1)) + 1.0 ForestDavis4_delta((TrackOne,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackEleven)_:  1.0 ForestDavis4_delta((TrackEleven,Ano1)) + 1.0 ForestDavis4_delta((TrackEleven,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackEleven)_:  1.0 ForestDavis4_delta((TrackEleven,Ano1)) + 1.0 ForestDavis4_delta((TrackEleven,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackThree)_:  1.0 ForestDavis4_delta((TrackThree,Ano1)) + 1.0 ForestDavis4_delta((TrackThree,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackThree)_:  1.0 ForestDavis4_delta((TrackThree,Ano1)) + 1.0 ForestDavis4_delta((TrackThree,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackTwentyFour)_:  1.0 ForestDavis4_delta((TrackTwentyFour,Ano1)) + 1.0 ForestDavis4_delta((TrackTwentyFour,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackTwentyFour)_:  1.0 ForestDavis4_delta((TrackTwentyFour,Ano1)) + 1.0 ForestDavis4_delta((TrackTwentyFour,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackSeventeen)_:  1.0 ForestDavis4_delta((TrackSeventeen,Ano1)) + 1.0 ForestDavis4_delta((TrackSeventeen,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackSeventeen)_:  1.0 ForestDavis4_delta((TrackSeventeen,Ano1)) + 1.0 ForestDavis4_delta((TrackSeventeen,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackTwelve)_:  1.0 ForestDavis4_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis4_delta((TrackTwelve,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackTwelve)_:  1.0 ForestDavis4_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis4_delta((TrackTwelve,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackNineteen)_:  1.0 ForestDavis4_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis4_delta((TrackNineteen,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackNineteen)_:  1.0 ForestDavis4_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis4_delta((TrackNineteen,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackTen)_:  1.0 ForestDavis4_delta((TrackTen,Ano1)) + 1.0 ForestDavis4_delta((TrackTen,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackTen)_:  1.0 ForestDavis4_delta((TrackTen,Ano1)) + 1.0 ForestDavis4_delta((TrackTen,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackThirteen)_:  1.0 ForestDavis4_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis4_delta((TrackThirteen,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackThirteen)_:  1.0 ForestDavis4_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis4_delta((TrackThirteen,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackTwenty)_:  1.0 ForestDavis4_delta((TrackTwenty,Ano1)) + 1.0 ForestDavis4_delta((TrackTwenty,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackTwenty)_:  1.0 ForestDavis4_delta((TrackTwenty,Ano1)) + 1.0 ForestDavis4_delta((TrackTwenty,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackTwentyTwo)_:  1.0 ForestDavis4_delta((TrackTwentyTwo,Ano1)) + 1.0 ForestDavis4_delta((TrackTwentyTwo,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackTwentyTwo)_:  1.0 ForestDavis4_delta((TrackTwentyTwo,Ano1)) + 1.0 ForestDavis4_delta((TrackTwentyTwo,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackSixteen)_:  1.0 ForestDavis4_delta((TrackSixteen,Ano1)) + 1.0 ForestDavis4_delta((TrackSixteen,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackSixteen)_:  1.0 ForestDavis4_delta((TrackSixteen,Ano1)) + 1.0 ForestDavis4_delta((TrackSixteen,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackTwo)_:  1.0 ForestDavis4_delta((TrackTwo,Ano1)) + 1.0 ForestDavis4_delta((TrackTwo,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackTwo)_:  1.0 ForestDavis4_delta((TrackTwo,Ano1)) + 1.0 ForestDavis4_delta((TrackTwo,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackSix)_:  1.0 ForestDavis4_delta((TrackSix,Ano1)) + 1.0 ForestDavis4_delta((TrackSix,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackSix)_:  1.0 ForestDavis4_delta((TrackSix,Ano1)) + 1.0 ForestDavis4_delta((TrackSix,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackSeven)_:  1.0 ForestDavis4_delta((TrackSeven,Ano1)) + 1.0 ForestDavis4_delta((TrackSeven,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackSeven)_:  1.0 ForestDavis4_delta((TrackSeven,Ano1)) + 1.0 ForestDavis4_delta((TrackSeven,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackFifteen)_:  1.0 ForestDavis4_delta((TrackFifteen,Ano1)) + 1.0 ForestDavis4_delta((TrackFifteen,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackFifteen)_:  1.0 ForestDavis4_delta((TrackFifteen,Ano1)) + 1.0 ForestDavis4_delta((TrackFifteen,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackFour)_:  1.0 ForestDavis4_delta((TrackFour,Ano1)) + 1.0 ForestDavis4_delta((TrackFour,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackFour)_:  1.0 ForestDavis4_delta((TrackFour,Ano1)) + 1.0 ForestDavis4_delta((TrackFour,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackFourteen)_:  1.0 ForestDavis4_delta((TrackFourteen,Ano1)) + 1.0 ForestDavis4_delta((TrackFourteen,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackFourteen)_:  1.0 ForestDavis4_delta((TrackFourteen,Ano1)) + 1.0 ForestDavis4_delta((TrackFourteen,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackTwentyOne)_:  1.0 ForestDavis4_delta((TrackTwentyOne,Ano1)) + 1.0 ForestDavis4_delta((TrackTwentyOne,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackTwentyOne)_:  1.0 ForestDavis4_delta((TrackTwentyOne,Ano1)) + 1.0 ForestDavis4_delta((TrackTwentyOne,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackEighteen)_:  1.0 ForestDavis4_delta((TrackEighteen,Ano1)) + 1.0 ForestDavis4_delta((TrackEighteen,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackEighteen)_:  1.0 ForestDavis4_delta((TrackEighteen,Ano1)) + 1.0 ForestDavis4_delta((TrackEighteen,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackFive)_:  1.0 ForestDavis4_delta((TrackFive,Ano1)) + 1.0 ForestDavis4_delta((TrackFive,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackFive)_:  1.0 ForestDavis4_delta((TrackFive,Ano1)) + 1.0 ForestDavis4_delta((TrackFive,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackTwentyFive)_:  1.0 ForestDavis4_delta((TrackTwentyFive,Ano1)) + 1.0 ForestDavis4_delta((TrackTwentyFive,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackTwentyFive)_:  1.0 ForestDavis4_delta((TrackTwentyFive,Ano1)) + 1.0 ForestDavis4_delta((TrackTwentyFive,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOneHarvest(TrackEight)_:  1.0 ForestDavis4_delta((TrackEight,Ano1)) + 1.0 ForestDavis4_delta((TrackEight,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOneHarvest(TrackEight)_:  1.0 ForestDavis4_delta((TrackEight,Ano1)) + 1.0 ForestDavis4_delta((TrackEight,Ano2)) <= 1.0

ForestDavis4_c_e_ComputeStageProfit(Ano1)_:  1.0 ForestDavis4_AnoProfit(Ano1) + 711000.0 ForestDavis4_delta((TrackEight,Ano1)) + 447000.0 ForestDavis4_delta((TrackEighteen,Ano1)) + 507000.0 ForestDavis4_delta((TrackEleven,Ano1)) + 618750.0 ForestDavis4_delta((TrackFifteen,Ano1)) 
+ 560000.0 ForestDavis4_delta((TrackFive,Ano1)) + 375000.0 ForestDavis4_delta((TrackFour,Ano1)) + 387500.0 ForestDavis4_delta((TrackFourteen,Ano1)) + 453750.0 ForestDavis4_delta((TrackNine,Ano1)) + 275000.0 ForestDavis4_delta((TrackNineteen,Ano1)) 
+ 412500.0 ForestDavis4_delta((TrackOne,Ano1)) + 461250.0 ForestDavis4_delta((TrackSeven,Ano1)) + 535500.0 ForestDavis4_delta((TrackSeventeen,Ano1)) + 656250.0 ForestDavis4_delta((TrackSix,Ano1)) + 561000.0 ForestDavis4_delta((TrackSixteen,Ano1)) 
+ 656250.0 ForestDavis4_delta((TrackTen,Ano1)) + 386750.0 ForestDavis4_delta((TrackThirteen,Ano1)) + 375000.0 ForestDavis4_delta((TrackThree,Ano1)) + 630000.0 ForestDavis4_delta((TrackTwelve,Ano1)) + 326250.0 ForestDavis4_delta((TrackTwenty,Ano1)) 
+ 393750.0 ForestDavis4_delta((TrackTwentyFive,Ano1)) + 330000.0 ForestDavis4_delta((TrackTwentyFour,Ano1)) + 468750.0 ForestDavis4_delta((TrackTwentyOne,Ano1)) + 315000.0 ForestDavis4_delta((TrackTwentyThree,Ano1)) + 431250.0 ForestDavis4_delta((TrackTwentyTwo,Ano1)) 
+ 400000.0 ForestDavis4_delta((TrackTwo,Ano1)) + 20.0 ForestDavis4_f((Int1Exit1P,Ano1)) + 17.0 ForestDavis4_f((Int1Int2E,Ano1)) + 14.0 ForestDavis4_f((Int1Int3P,Ano1)) + 10.0 ForestDavis4_f((Int1Org5P,Ano1)) 
+ 8.0 ForestDavis4_f((Int2Exit1E,Ano1)) + 15.0 ForestDavis4_f((Int3Exit1E,Ano1)) + 10.0 ForestDavis4_f((Org1Int3P,Ano1)) + 5.0 ForestDavis4_f((Org1Org2P,Ano1)) + 14.0 ForestDavis4_f((Org1Org3P,Ano1)) 
+ 21.0 ForestDavis4_f((Org2Exit1P,Ano1)) + 5.0 ForestDavis4_f((Org2Int3E,Ano1)) + 5.0 ForestDavis4_f((Org3Int1P,Ano1)) + 8.0 ForestDavis4_f((Org4Int1P,Ano1)) + 15.0 ForestDavis4_f((Org4Org9P,Ano1)) 
+ 12.0 ForestDavis4_f((Org5Exit1E,Ano1)) + 12.0 ForestDavis4_f((Org6Exit1P,Ano1)) + 15.0 ForestDavis4_f((Org7Exit1P,Ano1)) + 8.0 ForestDavis4_f((Org7Int2E,Ano1)) + 5.0 ForestDavis4_f((Org8Exit1P,Ano1)) 
+ 8.0 ForestDavis4_f((Org9Int2P,Ano1)) + 1800.0 ForestDavis4_gamma((Int1Exit1P,Ano1)) + 1750.0 ForestDavis4_gamma((Int1Int3P,Ano1)) + 1050.0 ForestDavis4_gamma((Int1Org5P,Ano1)) + 1110.0 ForestDavis4_gamma((Org1Int3P,Ano1)) 
+ 900.0 ForestDavis4_gamma((Org1Org2P,Ano1)) + 1200.0 ForestDavis4_gamma((Org1Org3P,Ano1)) + 2840.0 ForestDavis4_gamma((Org2Exit1P,Ano1)) + 900.0 ForestDavis4_gamma((Org3Int1P,Ano1)) + 1050.0 ForestDavis4_gamma((Org4Int1P,Ano1)) 
+ 1750.0 ForestDavis4_gamma((Org4Org9P,Ano1)) + 1550.0 ForestDavis4_gamma((Org6Exit1P,Ano1)) + 1750.0 ForestDavis4_gamma((Org7Exit1P,Ano1)) + 990.0 ForestDavis4_gamma((Org8Exit1P,Ano1)) + 1200.0 ForestDavis4_gamma((Org9Int2P,Ano1)) 
- 45.0 ForestDavis4_z((Exit1,Ano1)) = 0.0

ForestDavis4_c_e_ComputeStageProfit(Ano2)_:  1.0 ForestDavis4_AnoProfit(Ano2) + 673560.0 ForestDavis4_delta((TrackEight,Ano2)) + 442320.0 ForestDavis4_delta((TrackEighteen,Ano2)) + 513120.0 ForestDavis4_delta((TrackEleven,Ano2)) + 590250.0 ForestDavis4_delta((TrackFifteen,Ano2)) 
+ 562380.0 ForestDavis4_delta((TrackFive,Ano2)) + 362900.0 ForestDavis4_delta((TrackFour,Ano2)) + 383200.0 ForestDavis4_delta((TrackFourteen,Ano2)) + 441650.0 ForestDavis4_delta((TrackNine,Ano2)) + 291500.0 ForestDavis4_delta((TrackNineteen,Ano2)) 
+ 418990.0 ForestDavis4_delta((TrackOne,Ano2)) + 454680.0 ForestDavis4_delta((TrackSeven,Ano2)) + 529620.0 ForestDavis4_delta((TrackSeventeen,Ano2)) + 631200.0 ForestDavis4_delta((TrackSix,Ano2)) + 538800.0 ForestDavis4_delta((TrackSixteen,Ano2)) 
+ 651450.0 ForestDavis4_delta((TrackTen,Ano2)) + 389270.0 ForestDavis4_delta((TrackThirteen,Ano2)) + 374900.0 ForestDavis4_delta((TrackThree,Ano2)) + 608040.0 ForestDavis4_delta((TrackTwelve,Ano2)) + 323820.0 ForestDavis4_delta((TrackTwenty,Ano2)) 
+ 392550.0 ForestDavis4_delta((TrackTwentyFive,Ano2)) + 334480.0 ForestDavis4_delta((TrackTwentyFour,Ano2)) + 476400.0 ForestDavis4_delta((TrackTwentyOne,Ano2)) + 310950.0 ForestDavis4_delta((TrackTwentyThree,Ano2)) + 426600.0 ForestDavis4_delta((TrackTwentyTwo,Ano2)) 
+ 405100.0 ForestDavis4_delta((TrackTwo,Ano2)) + 20.0 ForestDavis4_f((Int1Exit1P,Ano2)) + 17.0 ForestDavis4_f((Int1Int2E,Ano2)) + 14.0 ForestDavis4_f((Int1Int3P,Ano2)) + 10.0 ForestDavis4_f((Int1Org5P,Ano2)) 
+ 8.0 ForestDavis4_f((Int2Exit1E,Ano2)) + 15.0 ForestDavis4_f((Int3Exit1E,Ano2)) + 10.0 ForestDavis4_f((Org1Int3P,Ano2)) + 5.0 ForestDavis4_f((Org1Org2P,Ano2)) + 14.0 ForestDavis4_f((Org1Org3P,Ano2)) 
+ 21.0 ForestDavis4_f((Org2Exit1P,Ano2)) + 5.0 ForestDavis4_f((Org2Int3E,Ano2)) + 5.0 ForestDavis4_f((Org3Int1P,Ano2)) + 8.0 ForestDavis4_f((Org4Int1P,Ano2)) + 15.0 ForestDavis4_f((Org4Org9P,Ano2)) 
+ 12.0 ForestDavis4_f((Org5Exit1E,Ano2)) + 12.0 ForestDavis4_f((Org6Exit1P,Ano2)) + 15.0 ForestDavis4_f((Org7Exit1P,Ano2)) + 8.0 ForestDavis4_f((Org7Int2E,Ano2)) + 5.0 ForestDavis4_f((Org8Exit1P,Ano2)) 
+ 8.0 ForestDavis4_f((Org9Int2P,Ano2)) + 1636.0 ForestDavis4_gamma((Int1Exit1P,Ano2)) + 1591.0 ForestDavis4_gamma((Int1Int3P,Ano2)) + 955.0 ForestDavis4_gamma((Int1Org5P,Ano2)) + 1009.0 ForestDavis4_gamma((Org1Int3P,Ano2)) 
+ 818.0 ForestDavis4_gamma((Org1Org2P,Ano2)) + 1091.0 ForestDavis4_gamma((Org1Org3P,Ano2)) + 2582.0 ForestDavis4_gamma((Org2Exit1P,Ano2)) + 818.0 ForestDavis4_gamma((Org3Int1P,Ano2)) + 955.0 ForestDavis4_gamma((Org4Int1P,Ano2)) 
+ 1591.0 ForestDavis4_gamma((Org4Org9P,Ano2)) + 1409.0 ForestDavis4_gamma((Org6Exit1P,Ano2)) + 1591.0 ForestDavis4_gamma((Org7Exit1P,Ano2)) + 900.0 ForestDavis4_gamma((Org8Exit1P,Ano2)) + 1091.0 ForestDavis4_gamma((Org9Int2P,Ano2)) 
- 60.0 ForestDavis4_z((Exit1,Ano2)) = 0.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org1Org2P)_:  1.0 ForestDavis4_gamma((Org1Org2P,Ano1)) + 1.0 ForestDavis4_gamma((Org1Org2P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org1Org2P)_:  1.0 ForestDavis4_gamma((Org1Org2P,Ano1)) + 1.0 ForestDavis4_gamma((Org1Org2P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org6Exit1P)_:  1.0 ForestDavis4_gamma((Org6Exit1P,Ano1)) + 1.0 ForestDavis4_gamma((Org6Exit1P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org6Exit1P)_:  1.0 ForestDavis4_gamma((Org6Exit1P,Ano1)) + 1.0 ForestDavis4_gamma((Org6Exit1P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org3Int1P)_:  1.0 ForestDavis4_gamma((Org3Int1P,Ano1)) + 1.0 ForestDavis4_gamma((Org3Int1P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org3Int1P)_:  1.0 ForestDavis4_gamma((Org3Int1P,Ano1)) + 1.0 ForestDavis4_gamma((Org3Int1P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org4Int1P)_:  1.0 ForestDavis4_gamma((Org4Int1P,Ano1)) + 1.0 ForestDavis4_gamma((Org4Int1P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org4Int1P)_:  1.0 ForestDavis4_gamma((Org4Int1P,Ano1)) + 1.0 ForestDavis4_gamma((Org4Int1P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org7Exit1P)_:  1.0 ForestDavis4_gamma((Org7Exit1P,Ano1)) + 1.0 ForestDavis4_gamma((Org7Exit1P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org7Exit1P)_:  1.0 ForestDavis4_gamma((Org7Exit1P,Ano1)) + 1.0 ForestDavis4_gamma((Org7Exit1P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org2Exit1P)_:  1.0 ForestDavis4_gamma((Org2Exit1P,Ano1)) + 1.0 ForestDavis4_gamma((Org2Exit1P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org2Exit1P)_:  1.0 ForestDavis4_gamma((Org2Exit1P,Ano1)) + 1.0 ForestDavis4_gamma((Org2Exit1P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org1Int3P)_:  1.0 ForestDavis4_gamma((Org1Int3P,Ano1)) + 1.0 ForestDavis4_gamma((Org1Int3P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org1Int3P)_:  1.0 ForestDavis4_gamma((Org1Int3P,Ano1)) + 1.0 ForestDavis4_gamma((Org1Int3P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Int1Exit1P)_:  1.0 ForestDavis4_gamma((Int1Exit1P,Ano1)) + 1.0 ForestDavis4_gamma((Int1Exit1P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Int1Exit1P)_:  1.0 ForestDavis4_gamma((Int1Exit1P,Ano1)) + 1.0 ForestDavis4_gamma((Int1Exit1P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org1Org3P)_:  1.0 ForestDavis4_gamma((Org1Org3P,Ano1)) + 1.0 ForestDavis4_gamma((Org1Org3P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org1Org3P)_:  1.0 ForestDavis4_gamma((Org1Org3P,Ano1)) + 1.0 ForestDavis4_gamma((Org1Org3P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org4Org9P)_:  1.0 ForestDavis4_gamma((Org4Org9P,Ano1)) + 1.0 ForestDavis4_gamma((Org4Org9P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org4Org9P)_:  1.0 ForestDavis4_gamma((Org4Org9P,Ano1)) + 1.0 ForestDavis4_gamma((Org4Org9P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Int1Org5P)_:  1.0 ForestDavis4_gamma((Int1Org5P,Ano1)) + 1.0 ForestDavis4_gamma((Int1Org5P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Int1Org5P)_:  1.0 ForestDavis4_gamma((Int1Org5P,Ano1)) + 1.0 ForestDavis4_gamma((Int1Org5P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org8Exit1P)_:  1.0 ForestDavis4_gamma((Org8Exit1P,Ano1)) + 1.0 ForestDavis4_gamma((Org8Exit1P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org8Exit1P)_:  1.0 ForestDavis4_gamma((Org8Exit1P,Ano1)) + 1.0 ForestDavis4_gamma((Org8Exit1P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Org9Int2P)_:  1.0 ForestDavis4_gamma((Org9Int2P,Ano1)) + 1.0 ForestDavis4_gamma((Org9Int2P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Org9Int2P)_:  1.0 ForestDavis4_gamma((Org9Int2P,Ano1)) + 1.0 ForestDavis4_gamma((Org9Int2P,Ano2)) <= 1.0

ForestDavis4_c_l_EnforceOnePotentialRoad(Int1Int3P)_:  1.0 ForestDavis4_gamma((Int1Int3P,Ano1)) + 1.0 ForestDavis4_gamma((Int1Int3P,Ano2)) >= 0.0

ForestDavis4_c_u_EnforceOnePotentialRoad(Int1Int3P)_:  1.0 ForestDavis4_gamma((Int1Int3P,Ano1)) + 1.0 ForestDavis4_gamma((Int1Int3P,Ano2)) <= 1.0

c_e_ONE_VAR_CONSTANT: ONE_VAR_CONSTANT = 1.0

\ End constraint block for scenario ForestDavis4

\ Begin constraint block for scenario ForestDavis16
ForestDavis16_c_e_EnforceOriginFlowBalance((Origin5,Ano1))_:  15000.0 ForestDavis16_delta((TrackFourteen,Ano1)) + 17500.0 ForestDavis16_delta((TrackSeventeen,Ano1)) + 19950.0 ForestDavis16_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis16_f((Int1Org5P,Ano1)) - 1.0 ForestDavis16_f((Org5Exit1E,Ano1)) 
= 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin5,Ano2))_:  15700.0 ForestDavis16_delta((TrackFourteen,Ano2)) + 18760.0 ForestDavis16_delta((TrackSeventeen,Ano2)) + 20650.0 ForestDavis16_delta((TrackThirteen,Ano2)) + 1.0 ForestDavis16_f((Int1Org5P,Ano2)) - 1.0 ForestDavis16_f((Org5Exit1E,Ano2)) 
= 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin4,Ano1))_:  17500.0 ForestDavis16_delta((TrackFive,Ano1)) + 16500.0 ForestDavis16_delta((TrackNine,Ano1)) + 18750.0 ForestDavis16_delta((TrackTen,Ano1)) - 1.0 ForestDavis16_f((Org4Int1P,Ano1)) - 1.0 ForestDavis16_f((Org4Org9P,Ano1)) 
= 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin4,Ano2))_:  19460.0 ForestDavis16_delta((TrackFive,Ano2)) + 16940.0 ForestDavis16_delta((TrackNine,Ano2)) + 20700.0 ForestDavis16_delta((TrackTen,Ano2)) - 1.0 ForestDavis16_f((Org4Int1P,Ano2)) - 1.0 ForestDavis16_f((Org4Org9P,Ano2)) 
= 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin7,Ano1))_:  18000.0 ForestDavis16_delta((TrackTwenty,Ano1)) + 18750.0 ForestDavis16_delta((TrackTwentyFive,Ano1)) + 20000.0 ForestDavis16_delta((TrackTwentyFour,Ano1)) - 1.0 ForestDavis16_f((Org7Exit1P,Ano1)) - 1.0 ForestDavis16_f((Org7Int2E,Ano1)) 
= 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin7,Ano2))_:  18180.0 ForestDavis16_delta((TrackTwenty,Ano2)) + 19350.0 ForestDavis16_delta((TrackTwentyFive,Ano2)) + 20480.0 ForestDavis16_delta((TrackTwentyFour,Ano2)) - 1.0 ForestDavis16_f((Org7Exit1P,Ano2)) - 1.0 ForestDavis16_f((Org7Int2E,Ano2)) 
= 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin6,Ano1))_:  19800.0 ForestDavis16_delta((TrackSixteen,Ano1)) + 18750.0 ForestDavis16_delta((TrackTwentyOne,Ano1)) - 1.0 ForestDavis16_f((Org6Exit1P,Ano1)) = 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin6,Ano2))_:  19920.0 ForestDavis16_delta((TrackSixteen,Ano2)) + 20400.0 ForestDavis16_delta((TrackTwentyOne,Ano2)) - 1.0 ForestDavis16_f((Org6Exit1P,Ano2)) = 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin1,Ano1))_:  16500.0 ForestDavis16_delta((TrackOne,Ano1)) + 18750.0 ForestDavis16_delta((TrackSix,Ano1)) + 15000.0 ForestDavis16_delta((TrackTwo,Ano1)) - 1.0 ForestDavis16_f((Org1Int3P,Ano1)) - 1.0 ForestDavis16_f((Org1Org2P,Ano1)) 
- 1.0 ForestDavis16_f((Org1Org3P,Ano1)) = 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin1,Ano2))_:  17930.0 ForestDavis16_delta((TrackOne,Ano2)) + 19350.0 ForestDavis16_delta((TrackSix,Ano2)) + 16400.0 ForestDavis16_delta((TrackTwo,Ano2)) - 1.0 ForestDavis16_f((Org1Int3P,Ano2)) - 1.0 ForestDavis16_f((Org1Org2P,Ano2)) 
- 1.0 ForestDavis16_f((Org1Org3P,Ano2)) = 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin3,Ano1))_:  18000.0 ForestDavis16_delta((TrackEight,Ano1)) + 15000.0 ForestDavis16_delta((TrackFour,Ano1)) + 15000.0 ForestDavis16_delta((TrackThree,Ano1)) + 1.0 ForestDavis16_f((Org1Org3P,Ano1)) - 1.0 ForestDavis16_f((Org3Int1P,Ano1)) 
= 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin3,Ano2))_:  18180.0 ForestDavis16_delta((TrackEight,Ano2)) + 15100.0 ForestDavis16_delta((TrackFour,Ano2)) + 15900.0 ForestDavis16_delta((TrackThree,Ano2)) + 1.0 ForestDavis16_f((Org1Org3P,Ano2)) - 1.0 ForestDavis16_f((Org3Int1P,Ano2)) 
= 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin2,Ano1))_:  19800.0 ForestDavis16_delta((TrackEleven,Ano1)) + 18000.0 ForestDavis16_delta((TrackSeven,Ano1)) + 18000.0 ForestDavis16_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis16_f((Org1Org2P,Ano1)) - 1.0 ForestDavis16_f((Org2Exit1P,Ano1)) 
- 1.0 ForestDavis16_f((Org2Int3E,Ano1)) = 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin2,Ano2))_:  21480.0 ForestDavis16_delta((TrackEleven,Ano2)) + 18720.0 ForestDavis16_delta((TrackSeven,Ano2)) + 18720.0 ForestDavis16_delta((TrackTwelve,Ano2)) + 1.0 ForestDavis16_f((Org1Org2P,Ano2)) - 1.0 ForestDavis16_f((Org2Exit1P,Ano2)) 
- 1.0 ForestDavis16_f((Org2Int3E,Ano2)) = 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin9,Ano1))_:  19800.0 ForestDavis16_delta((TrackEighteen,Ano1)) + 18750.0 ForestDavis16_delta((TrackFifteen,Ano1)) + 15000.0 ForestDavis16_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis16_f((Org4Org9P,Ano1)) - 1.0 ForestDavis16_f((Org9Int2P,Ano1)) 
= 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin9,Ano2))_:  20400.0 ForestDavis16_delta((TrackEighteen,Ano2)) + 18900.0 ForestDavis16_delta((TrackFifteen,Ano2)) + 16400.0 ForestDavis16_delta((TrackNineteen,Ano2)) + 1.0 ForestDavis16_f((Org4Org9P,Ano2)) - 1.0 ForestDavis16_f((Org9Int2P,Ano2)) 
= 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin8,Ano1))_:  18000.0 ForestDavis16_delta((TrackTwentyThree,Ano1)) + 18750.0 ForestDavis16_delta((TrackTwentyTwo,Ano1)) - 1.0 ForestDavis16_f((Org8Exit1P,Ano1)) = 0.0

ForestDavis16_c_e_EnforceOriginFlowBalance((Origin8,Ano2))_:  18000.0 ForestDavis16_delta((TrackTwentyThree,Ano2)) + 19350.0 ForestDavis16_delta((TrackTwentyTwo,Ano2)) - 1.0 ForestDavis16_f((Org8Exit1P,Ano2)) = 0.0

ForestDavis16_c_l_EnforceWoodProductionBounds(Ano1)_:  1.0 ForestDavis16_z((Exit1,Ano1)) >= 30000.0

ForestDavis16_c_u_EnforceWoodProductionBounds(Ano1)_:  1.0 ForestDavis16_z((Exit1,Ano1)) <= 40000.0

ForestDavis16_c_l_EnforceWoodProductionBounds(Ano2)_:  1.0 ForestDavis16_z((Exit1,Ano2)) >= 10000.0

ForestDavis16_c_u_EnforceWoodProductionBounds(Ano2)_:  1.0 ForestDavis16_z((Exit1,Ano2)) <= 18000.0

ForestDavis16_c_e_EnforceDestinationFlowBalance((Exit1,Ano1))_:  -1.0 ForestDavis16_f((Int1Exit1P,Ano1)) - 1.0 ForestDavis16_f((Int2Exit1E,Ano1)) - 1.0 ForestDavis16_f((Int3Exit1E,Ano1)) - 1.0 ForestDavis16_f((Org2Exit1P,Ano1)) - 1.0 ForestDavis16_f((Org5Exit1E,Ano1)) 
- 1.0 ForestDavis16_f((Org6Exit1P,Ano1)) - 1.0 ForestDavis16_f((Org7Exit1P,Ano1)) - 1.0 ForestDavis16_f((Org8Exit1P,Ano1)) + 1.0 ForestDavis16_z((Exit1,Ano1)) = 0.0

ForestDavis16_c_e_EnforceDestinationFlowBalance((Exit1,Ano2))_:  -1.0 ForestDavis16_f((Int1Exit1P,Ano2)) - 1.0 ForestDavis16_f((Int2Exit1E,Ano2)) - 1.0 ForestDavis16_f((Int3Exit1E,Ano2)) - 1.0 ForestDavis16_f((Org2Exit1P,Ano2)) - 1.0 ForestDavis16_f((Org5Exit1E,Ano2)) 
- 1.0 ForestDavis16_f((Org6Exit1P,Ano2)) - 1.0 ForestDavis16_f((Org7Exit1P,Ano2)) - 1.0 ForestDavis16_f((Org8Exit1P,Ano2)) + 1.0 ForestDavis16_z((Exit1,Ano2)) = 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org1Org2P,Ano1))_:  1.0 ForestDavis16_f((Org1Org2P,Ano1)) - 15000.0 ForestDavis16_gamma((Org1Org2P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org1Org2P,Ano2))_:  1.0 ForestDavis16_f((Org1Org2P,Ano2)) - 16400.0 ForestDavis16_gamma((Org1Org2P,Ano1)) - 16400.0 ForestDavis16_gamma((Org1Org2P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org6Exit1P,Ano1))_:  1.0 ForestDavis16_f((Org6Exit1P,Ano1)) - 19800.0 ForestDavis16_gamma((Org6Exit1P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org6Exit1P,Ano2))_:  1.0 ForestDavis16_f((Org6Exit1P,Ano2)) - 20400.0 ForestDavis16_gamma((Org6Exit1P,Ano1)) - 20400.0 ForestDavis16_gamma((Org6Exit1P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org3Int1P,Ano1))_:  1.0 ForestDavis16_f((Org3Int1P,Ano1)) - 15000.0 ForestDavis16_gamma((Org3Int1P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org3Int1P,Ano2))_:  1.0 ForestDavis16_f((Org3Int1P,Ano2)) - 15100.0 ForestDavis16_gamma((Org3Int1P,Ano1)) - 15100.0 ForestDavis16_gamma((Org3Int1P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org4Int1P,Ano1))_:  1.0 ForestDavis16_f((Org4Int1P,Ano1)) - 17583.0 ForestDavis16_gamma((Org4Int1P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org4Int1P,Ano2))_:  1.0 ForestDavis16_f((Org4Int1P,Ano2)) - 19033.0 ForestDavis16_gamma((Org4Int1P,Ano1)) - 19033.0 ForestDavis16_gamma((Org4Int1P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org7Exit1P,Ano1))_:  1.0 ForestDavis16_f((Org7Exit1P,Ano1)) - 20000.0 ForestDavis16_gamma((Org7Exit1P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org7Exit1P,Ano2))_:  1.0 ForestDavis16_f((Org7Exit1P,Ano2)) - 20480.0 ForestDavis16_gamma((Org7Exit1P,Ano1)) - 20480.0 ForestDavis16_gamma((Org7Exit1P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org2Exit1P,Ano1))_:  1.0 ForestDavis16_f((Org2Exit1P,Ano1)) - 19800.0 ForestDavis16_gamma((Org2Exit1P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org2Exit1P,Ano2))_:  1.0 ForestDavis16_f((Org2Exit1P,Ano2)) - 21480.0 ForestDavis16_gamma((Org2Exit1P,Ano1)) - 21480.0 ForestDavis16_gamma((Org2Exit1P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org1Int3P,Ano1))_:  1.0 ForestDavis16_f((Org1Int3P,Ano1)) - 18750.0 ForestDavis16_gamma((Org1Int3P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org1Int3P,Ano2))_:  1.0 ForestDavis16_f((Org1Int3P,Ano2)) - 19350.0 ForestDavis16_gamma((Org1Int3P,Ano1)) - 19350.0 ForestDavis16_gamma((Org1Int3P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Int1Exit1P,Ano1))_:  1.0 ForestDavis16_f((Int1Exit1P,Ano1)) - 17583.0 ForestDavis16_gamma((Int1Exit1P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Int1Exit1P,Ano2))_:  1.0 ForestDavis16_f((Int1Exit1P,Ano2)) - 19033.0 ForestDavis16_gamma((Int1Exit1P,Ano1)) - 19033.0 ForestDavis16_gamma((Int1Exit1P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org1Org3P,Ano1))_:  1.0 ForestDavis16_f((Org1Org3P,Ano1)) - 18750.0 ForestDavis16_gamma((Org1Org3P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org1Org3P,Ano2))_:  1.0 ForestDavis16_f((Org1Org3P,Ano2)) - 19350.0 ForestDavis16_gamma((Org1Org3P,Ano1)) - 19350.0 ForestDavis16_gamma((Org1Org3P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org4Org9P,Ano1))_:  1.0 ForestDavis16_f((Org4Org9P,Ano1)) - 18750.0 ForestDavis16_gamma((Org4Org9P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org4Org9P,Ano2))_:  1.0 ForestDavis16_f((Org4Org9P,Ano2)) - 20700.0 ForestDavis16_gamma((Org4Org9P,Ano1)) - 20700.0 ForestDavis16_gamma((Org4Org9P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Int1Org5P,Ano1))_:  1.0 ForestDavis16_f((Int1Org5P,Ano1)) - 17583.0 ForestDavis16_gamma((Int1Org5P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Int1Org5P,Ano2))_:  1.0 ForestDavis16_f((Int1Org5P,Ano2)) - 19033.0 ForestDavis16_gamma((Int1Org5P,Ano1)) - 19033.0 ForestDavis16_gamma((Int1Org5P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org8Exit1P,Ano1))_:  1.0 ForestDavis16_f((Org8Exit1P,Ano1)) - 18750.0 ForestDavis16_gamma((Org8Exit1P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org8Exit1P,Ano2))_:  1.0 ForestDavis16_f((Org8Exit1P,Ano2)) - 19350.0 ForestDavis16_gamma((Org8Exit1P,Ano1)) - 19350.0 ForestDavis16_gamma((Org8Exit1P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org9Int2P,Ano1))_:  1.0 ForestDavis16_f((Org9Int2P,Ano1)) - 19800.0 ForestDavis16_gamma((Org9Int2P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Org9Int2P,Ano2))_:  1.0 ForestDavis16_f((Org9Int2P,Ano2)) - 20400.0 ForestDavis16_gamma((Org9Int2P,Ano1)) - 20400.0 ForestDavis16_gamma((Org9Int2P,Ano2)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Int1Int3P,Ano1))_:  1.0 ForestDavis16_f((Int1Int3P,Ano1)) - 17583.0 ForestDavis16_gamma((Int1Int3P,Ano1)) <= 0.0

ForestDavis16_c_u_EnforcePotentialRoadFlowCap((Int1Int3P,Ano2))_:  1.0 ForestDavis16_f((Int1Int3P,Ano2)) - 19033.0 ForestDavis16_gamma((Int1Int3P,Ano1)) - 19033.0 ForestDavis16_gamma((Int1Int3P,Ano2)) <= 0.0

ForestDavis16_c_e_EnforceIntersectionFlowBalance((Intersection1,Ano1))_:  -1.0 ForestDavis16_f((Int1Exit1P,Ano1)) - 1.0 ForestDavis16_f((Int1Int2E,Ano1)) - 1.0 ForestDavis16_f((Int1Int3P,Ano1)) - 1.0 ForestDavis16_f((Int1Org5P,Ano1)) + 1.0 ForestDavis16_f((Org3Int1P,Ano1)) 
+ 1.0 ForestDavis16_f((Org4Int1P,Ano1)) = 0.0

ForestDavis16_c_e_EnforceIntersectionFlowBalance((Intersection1,Ano2))_:  -1.0 ForestDavis16_f((Int1Exit1P,Ano2)) - 1.0 ForestDavis16_f((Int1Int2E,Ano2)) - 1.0 ForestDavis16_f((Int1Int3P,Ano2)) - 1.0 ForestDavis16_f((Int1Org5P,Ano2)) + 1.0 ForestDavis16_f((Org3Int1P,Ano2)) 
+ 1.0 ForestDavis16_f((Org4Int1P,Ano2)) = 0.0

ForestDavis16_c_e_EnforceIntersectionFlowBalance((Intersection2,Ano1))_:  1.0 ForestDavis16_f((Int1Int2E,Ano1)) - 1.0 ForestDavis16_f((Int2Exit1E,Ano1)) + 1.0 ForestDavis16_f((Org7Int2E,Ano1)) + 1.0 ForestDavis16_f((Org9Int2P,Ano1)) = 0.0

ForestDavis16_c_e_EnforceIntersectionFlowBalance((Intersection2,Ano2))_:  1.0 ForestDavis16_f((Int1Int2E,Ano2)) - 1.0 ForestDavis16_f((Int2Exit1E,Ano2)) + 1.0 ForestDavis16_f((Org7Int2E,Ano2)) + 1.0 ForestDavis16_f((Org9Int2P,Ano2)) = 0.0

ForestDavis16_c_e_EnforceIntersectionFlowBalance((Intersection3,Ano1))_:  1.0 ForestDavis16_f((Int1Int3P,Ano1)) - 1.0 ForestDavis16_f((Int3Exit1E,Ano1)) + 1.0 ForestDavis16_f((Org1Int3P,Ano1)) + 1.0 ForestDavis16_f((Org2Int3E,Ano1)) = 0.0

ForestDavis16_c_e_EnforceIntersectionFlowBalance((Intersection3,Ano2))_:  1.0 ForestDavis16_f((Int1Int3P,Ano2)) - 1.0 ForestDavis16_f((Int3Exit1E,Ano2)) + 1.0 ForestDavis16_f((Org1Int3P,Ano2)) + 1.0 ForestDavis16_f((Org2Int3E,Ano2)) = 0.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Int3Exit1E,Ano1))_:  1.0 ForestDavis16_f((Int3Exit1E,Ano1)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Int3Exit1E,Ano1))_:  1.0 ForestDavis16_f((Int3Exit1E,Ano1)) <= 17583.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Int3Exit1E,Ano2))_:  1.0 ForestDavis16_f((Int3Exit1E,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Int3Exit1E,Ano2))_:  1.0 ForestDavis16_f((Int3Exit1E,Ano2)) <= 18720.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Int1Int2E,Ano1))_:  1.0 ForestDavis16_f((Int1Int2E,Ano1)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Int1Int2E,Ano1))_:  1.0 ForestDavis16_f((Int1Int2E,Ano1)) <= 15000.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Int1Int2E,Ano2))_:  1.0 ForestDavis16_f((Int1Int2E,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Int1Int2E,Ano2))_:  1.0 ForestDavis16_f((Int1Int2E,Ano2)) <= 15100.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Org2Int3E,Ano1))_:  1.0 ForestDavis16_f((Org2Int3E,Ano1)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Org2Int3E,Ano1))_:  1.0 ForestDavis16_f((Org2Int3E,Ano1)) <= 18000.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Org2Int3E,Ano2))_:  1.0 ForestDavis16_f((Org2Int3E,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Org2Int3E,Ano2))_:  1.0 ForestDavis16_f((Org2Int3E,Ano2)) <= 18720.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Org7Int2E,Ano1))_:  1.0 ForestDavis16_f((Org7Int2E,Ano1)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Org7Int2E,Ano1))_:  1.0 ForestDavis16_f((Org7Int2E,Ano1)) <= 18000.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Org7Int2E,Ano2))_:  1.0 ForestDavis16_f((Org7Int2E,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Org7Int2E,Ano2))_:  1.0 ForestDavis16_f((Org7Int2E,Ano2)) <= 18180.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Org5Exit1E,Ano1))_:  1.0 ForestDavis16_f((Org5Exit1E,Ano1)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Org5Exit1E,Ano1))_:  1.0 ForestDavis16_f((Org5Exit1E,Ano1)) <= 15000.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Org5Exit1E,Ano2))_:  1.0 ForestDavis16_f((Org5Exit1E,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Org5Exit1E,Ano2))_:  1.0 ForestDavis16_f((Org5Exit1E,Ano2)) <= 15700.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Int2Exit1E,Ano1))_:  1.0 ForestDavis16_f((Int2Exit1E,Ano1)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Int2Exit1E,Ano1))_:  1.0 ForestDavis16_f((Int2Exit1E,Ano1)) <= 15000.0

ForestDavis16_c_l_EnforceExistingRoadCapacities((Int2Exit1E,Ano2))_:  1.0 ForestDavis16_f((Int2Exit1E,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceExistingRoadCapacities((Int2Exit1E,Ano2))_:  1.0 ForestDavis16_f((Int2Exit1E,Ano2)) <= 15100.0

ForestDavis16_c_l_EnforceOneHarvest(TrackNine)_:  1.0 ForestDavis16_delta((TrackNine,Ano1)) + 1.0 ForestDavis16_delta((TrackNine,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackNine)_:  1.0 ForestDavis16_delta((TrackNine,Ano1)) + 1.0 ForestDavis16_delta((TrackNine,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackTwentyThree)_:  1.0 ForestDavis16_delta((TrackTwentyThree,Ano1)) + 1.0 ForestDavis16_delta((TrackTwentyThree,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackTwentyThree)_:  1.0 ForestDavis16_delta((TrackTwentyThree,Ano1)) + 1.0 ForestDavis16_delta((TrackTwentyThree,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackOne)_:  1.0 ForestDavis16_delta((TrackOne,Ano1)) + 1.0 ForestDavis16_delta((TrackOne,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackOne)_:  1.0 ForestDavis16_delta((TrackOne,Ano1)) + 1.0 ForestDavis16_delta((TrackOne,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackEleven)_:  1.0 ForestDavis16_delta((TrackEleven,Ano1)) + 1.0 ForestDavis16_delta((TrackEleven,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackEleven)_:  1.0 ForestDavis16_delta((TrackEleven,Ano1)) + 1.0 ForestDavis16_delta((TrackEleven,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackThree)_:  1.0 ForestDavis16_delta((TrackThree,Ano1)) + 1.0 ForestDavis16_delta((TrackThree,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackThree)_:  1.0 ForestDavis16_delta((TrackThree,Ano1)) + 1.0 ForestDavis16_delta((TrackThree,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackTwentyFour)_:  1.0 ForestDavis16_delta((TrackTwentyFour,Ano1)) + 1.0 ForestDavis16_delta((TrackTwentyFour,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackTwentyFour)_:  1.0 ForestDavis16_delta((TrackTwentyFour,Ano1)) + 1.0 ForestDavis16_delta((TrackTwentyFour,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackSeventeen)_:  1.0 ForestDavis16_delta((TrackSeventeen,Ano1)) + 1.0 ForestDavis16_delta((TrackSeventeen,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackSeventeen)_:  1.0 ForestDavis16_delta((TrackSeventeen,Ano1)) + 1.0 ForestDavis16_delta((TrackSeventeen,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackTwelve)_:  1.0 ForestDavis16_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis16_delta((TrackTwelve,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackTwelve)_:  1.0 ForestDavis16_delta((TrackTwelve,Ano1)) + 1.0 ForestDavis16_delta((TrackTwelve,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackNineteen)_:  1.0 ForestDavis16_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis16_delta((TrackNineteen,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackNineteen)_:  1.0 ForestDavis16_delta((TrackNineteen,Ano1)) + 1.0 ForestDavis16_delta((TrackNineteen,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackTen)_:  1.0 ForestDavis16_delta((TrackTen,Ano1)) + 1.0 ForestDavis16_delta((TrackTen,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackTen)_:  1.0 ForestDavis16_delta((TrackTen,Ano1)) + 1.0 ForestDavis16_delta((TrackTen,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackThirteen)_:  1.0 ForestDavis16_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis16_delta((TrackThirteen,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackThirteen)_:  1.0 ForestDavis16_delta((TrackThirteen,Ano1)) + 1.0 ForestDavis16_delta((TrackThirteen,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackTwenty)_:  1.0 ForestDavis16_delta((TrackTwenty,Ano1)) + 1.0 ForestDavis16_delta((TrackTwenty,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackTwenty)_:  1.0 ForestDavis16_delta((TrackTwenty,Ano1)) + 1.0 ForestDavis16_delta((TrackTwenty,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackTwentyTwo)_:  1.0 ForestDavis16_delta((TrackTwentyTwo,Ano1)) + 1.0 ForestDavis16_delta((TrackTwentyTwo,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackTwentyTwo)_:  1.0 ForestDavis16_delta((TrackTwentyTwo,Ano1)) + 1.0 ForestDavis16_delta((TrackTwentyTwo,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackSixteen)_:  1.0 ForestDavis16_delta((TrackSixteen,Ano1)) + 1.0 ForestDavis16_delta((TrackSixteen,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackSixteen)_:  1.0 ForestDavis16_delta((TrackSixteen,Ano1)) + 1.0 ForestDavis16_delta((TrackSixteen,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackTwo)_:  1.0 ForestDavis16_delta((TrackTwo,Ano1)) + 1.0 ForestDavis16_delta((TrackTwo,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackTwo)_:  1.0 ForestDavis16_delta((TrackTwo,Ano1)) + 1.0 ForestDavis16_delta((TrackTwo,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackSix)_:  1.0 ForestDavis16_delta((TrackSix,Ano1)) + 1.0 ForestDavis16_delta((TrackSix,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackSix)_:  1.0 ForestDavis16_delta((TrackSix,Ano1)) + 1.0 ForestDavis16_delta((TrackSix,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackSeven)_:  1.0 ForestDavis16_delta((TrackSeven,Ano1)) + 1.0 ForestDavis16_delta((TrackSeven,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackSeven)_:  1.0 ForestDavis16_delta((TrackSeven,Ano1)) + 1.0 ForestDavis16_delta((TrackSeven,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackFifteen)_:  1.0 ForestDavis16_delta((TrackFifteen,Ano1)) + 1.0 ForestDavis16_delta((TrackFifteen,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackFifteen)_:  1.0 ForestDavis16_delta((TrackFifteen,Ano1)) + 1.0 ForestDavis16_delta((TrackFifteen,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackFour)_:  1.0 ForestDavis16_delta((TrackFour,Ano1)) + 1.0 ForestDavis16_delta((TrackFour,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackFour)_:  1.0 ForestDavis16_delta((TrackFour,Ano1)) + 1.0 ForestDavis16_delta((TrackFour,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackFourteen)_:  1.0 ForestDavis16_delta((TrackFourteen,Ano1)) + 1.0 ForestDavis16_delta((TrackFourteen,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackFourteen)_:  1.0 ForestDavis16_delta((TrackFourteen,Ano1)) + 1.0 ForestDavis16_delta((TrackFourteen,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackTwentyOne)_:  1.0 ForestDavis16_delta((TrackTwentyOne,Ano1)) + 1.0 ForestDavis16_delta((TrackTwentyOne,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackTwentyOne)_:  1.0 ForestDavis16_delta((TrackTwentyOne,Ano1)) + 1.0 ForestDavis16_delta((TrackTwentyOne,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackEighteen)_:  1.0 ForestDavis16_delta((TrackEighteen,Ano1)) + 1.0 ForestDavis16_delta((TrackEighteen,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackEighteen)_:  1.0 ForestDavis16_delta((TrackEighteen,Ano1)) + 1.0 ForestDavis16_delta((TrackEighteen,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackFive)_:  1.0 ForestDavis16_delta((TrackFive,Ano1)) + 1.0 ForestDavis16_delta((TrackFive,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackFive)_:  1.0 ForestDavis16_delta((TrackFive,Ano1)) + 1.0 ForestDavis16_delta((TrackFive,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackTwentyFive)_:  1.0 ForestDavis16_delta((TrackTwentyFive,Ano1)) + 1.0 ForestDavis16_delta((TrackTwentyFive,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackTwentyFive)_:  1.0 ForestDavis16_delta((TrackTwentyFive,Ano1)) + 1.0 ForestDavis16_delta((TrackTwentyFive,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOneHarvest(TrackEight)_:  1.0 ForestDavis16_delta((TrackEight,Ano1)) + 1.0 ForestDavis16_delta((TrackEight,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOneHarvest(TrackEight)_:  1.0 ForestDavis16_delta((TrackEight,Ano1)) + 1.0 ForestDavis16_delta((TrackEight,Ano2)) <= 1.0

ForestDavis16_c_e_ComputeStageProfit(Ano1)_:  1.0 ForestDavis16_AnoProfit(Ano1) + 711000.0 ForestDavis16_delta((TrackEight,Ano1)) + 447000.0 ForestDavis16_delta((TrackEighteen,Ano1)) + 507000.0 ForestDavis16_delta((TrackEleven,Ano1)) + 618750.0 ForestDavis16_delta((TrackFifteen,Ano1)) 
+ 560000.0 ForestDavis16_delta((TrackFive,Ano1)) + 375000.0 ForestDavis16_delta((TrackFour,Ano1)) + 387500.0 ForestDavis16_delta((TrackFourteen,Ano1)) + 453750.0 ForestDavis16_delta((TrackNine,Ano1)) + 275000.0 ForestDavis16_delta((TrackNineteen,Ano1)) 
+ 412500.0 ForestDavis16_delta((TrackOne,Ano1)) + 461250.0 ForestDavis16_delta((TrackSeven,Ano1)) + 535500.0 ForestDavis16_delta((TrackSeventeen,Ano1)) + 656250.0 ForestDavis16_delta((TrackSix,Ano1)) + 561000.0 ForestDavis16_delta((TrackSixteen,Ano1)) 
+ 656250.0 ForestDavis16_delta((TrackTen,Ano1)) + 386750.0 ForestDavis16_delta((TrackThirteen,Ano1)) + 375000.0 ForestDavis16_delta((TrackThree,Ano1)) + 630000.0 ForestDavis16_delta((TrackTwelve,Ano1)) + 326250.0 ForestDavis16_delta((TrackTwenty,Ano1)) 
+ 393750.0 ForestDavis16_delta((TrackTwentyFive,Ano1)) + 330000.0 ForestDavis16_delta((TrackTwentyFour,Ano1)) + 468750.0 ForestDavis16_delta((TrackTwentyOne,Ano1)) + 315000.0 ForestDavis16_delta((TrackTwentyThree,Ano1)) + 431250.0 ForestDavis16_delta((TrackTwentyTwo,Ano1)) 
+ 400000.0 ForestDavis16_delta((TrackTwo,Ano1)) + 20.0 ForestDavis16_f((Int1Exit1P,Ano1)) + 17.0 ForestDavis16_f((Int1Int2E,Ano1)) + 14.0 ForestDavis16_f((Int1Int3P,Ano1)) + 10.0 ForestDavis16_f((Int1Org5P,Ano1)) 
+ 8.0 ForestDavis16_f((Int2Exit1E,Ano1)) + 15.0 ForestDavis16_f((Int3Exit1E,Ano1)) + 10.0 ForestDavis16_f((Org1Int3P,Ano1)) + 5.0 ForestDavis16_f((Org1Org2P,Ano1)) + 14.0 ForestDavis16_f((Org1Org3P,Ano1)) 
+ 21.0 ForestDavis16_f((Org2Exit1P,Ano1)) + 5.0 ForestDavis16_f((Org2Int3E,Ano1)) + 5.0 ForestDavis16_f((Org3Int1P,Ano1)) + 8.0 ForestDavis16_f((Org4Int1P,Ano1)) + 15.0 ForestDavis16_f((Org4Org9P,Ano1)) 
+ 12.0 ForestDavis16_f((Org5Exit1E,Ano1)) + 12.0 ForestDavis16_f((Org6Exit1P,Ano1)) + 15.0 ForestDavis16_f((Org7Exit1P,Ano1)) + 8.0 ForestDavis16_f((Org7Int2E,Ano1)) + 5.0 ForestDavis16_f((Org8Exit1P,Ano1)) 
+ 8.0 ForestDavis16_f((Org9Int2P,Ano1)) + 1800.0 ForestDavis16_gamma((Int1Exit1P,Ano1)) + 1750.0 ForestDavis16_gamma((Int1Int3P,Ano1)) + 1050.0 ForestDavis16_gamma((Int1Org5P,Ano1)) + 1110.0 ForestDavis16_gamma((Org1Int3P,Ano1)) 
+ 900.0 ForestDavis16_gamma((Org1Org2P,Ano1)) + 1200.0 ForestDavis16_gamma((Org1Org3P,Ano1)) + 2840.0 ForestDavis16_gamma((Org2Exit1P,Ano1)) + 900.0 ForestDavis16_gamma((Org3Int1P,Ano1)) + 1050.0 ForestDavis16_gamma((Org4Int1P,Ano1)) 
+ 1750.0 ForestDavis16_gamma((Org4Org9P,Ano1)) + 1550.0 ForestDavis16_gamma((Org6Exit1P,Ano1)) + 1750.0 ForestDavis16_gamma((Org7Exit1P,Ano1)) + 990.0 ForestDavis16_gamma((Org8Exit1P,Ano1)) + 1200.0 ForestDavis16_gamma((Org9Int2P,Ano1)) 
- 45.0 ForestDavis16_z((Exit1,Ano1)) = 0.0

ForestDavis16_c_e_ComputeStageProfit(Ano2)_:  1.0 ForestDavis16_AnoProfit(Ano2) + 673560.0 ForestDavis16_delta((TrackEight,Ano2)) + 442320.0 ForestDavis16_delta((TrackEighteen,Ano2)) + 513120.0 ForestDavis16_delta((TrackEleven,Ano2)) + 590250.0 ForestDavis16_delta((TrackFifteen,Ano2)) 
+ 562380.0 ForestDavis16_delta((TrackFive,Ano2)) + 362900.0 ForestDavis16_delta((TrackFour,Ano2)) + 383200.0 ForestDavis16_delta((TrackFourteen,Ano2)) + 441650.0 ForestDavis16_delta((TrackNine,Ano2)) + 291500.0 ForestDavis16_delta((TrackNineteen,Ano2)) 
+ 418990.0 ForestDavis16_delta((TrackOne,Ano2)) + 454680.0 ForestDavis16_delta((TrackSeven,Ano2)) + 529620.0 ForestDavis16_delta((TrackSeventeen,Ano2)) + 631200.0 ForestDavis16_delta((TrackSix,Ano2)) + 538800.0 ForestDavis16_delta((TrackSixteen,Ano2)) 
+ 651450.0 ForestDavis16_delta((TrackTen,Ano2)) + 389270.0 ForestDavis16_delta((TrackThirteen,Ano2)) + 374900.0 ForestDavis16_delta((TrackThree,Ano2)) + 608040.0 ForestDavis16_delta((TrackTwelve,Ano2)) + 323820.0 ForestDavis16_delta((TrackTwenty,Ano2)) 
+ 392550.0 ForestDavis16_delta((TrackTwentyFive,Ano2)) + 334480.0 ForestDavis16_delta((TrackTwentyFour,Ano2)) + 476400.0 ForestDavis16_delta((TrackTwentyOne,Ano2)) + 310950.0 ForestDavis16_delta((TrackTwentyThree,Ano2)) + 426600.0 ForestDavis16_delta((TrackTwentyTwo,Ano2)) 
+ 405100.0 ForestDavis16_delta((TrackTwo,Ano2)) + 20.0 ForestDavis16_f((Int1Exit1P,Ano2)) + 17.0 ForestDavis16_f((Int1Int2E,Ano2)) + 14.0 ForestDavis16_f((Int1Int3P,Ano2)) + 10.0 ForestDavis16_f((Int1Org5P,Ano2)) 
+ 8.0 ForestDavis16_f((Int2Exit1E,Ano2)) + 15.0 ForestDavis16_f((Int3Exit1E,Ano2)) + 10.0 ForestDavis16_f((Org1Int3P,Ano2)) + 5.0 ForestDavis16_f((Org1Org2P,Ano2)) + 14.0 ForestDavis16_f((Org1Org3P,Ano2)) 
+ 21.0 ForestDavis16_f((Org2Exit1P,Ano2)) + 5.0 ForestDavis16_f((Org2Int3E,Ano2)) + 5.0 ForestDavis16_f((Org3Int1P,Ano2)) + 8.0 ForestDavis16_f((Org4Int1P,Ano2)) + 15.0 ForestDavis16_f((Org4Org9P,Ano2)) 
+ 12.0 ForestDavis16_f((Org5Exit1E,Ano2)) + 12.0 ForestDavis16_f((Org6Exit1P,Ano2)) + 15.0 ForestDavis16_f((Org7Exit1P,Ano2)) + 8.0 ForestDavis16_f((Org7Int2E,Ano2)) + 5.0 ForestDavis16_f((Org8Exit1P,Ano2)) 
+ 8.0 ForestDavis16_f((Org9Int2P,Ano2)) + 1636.0 ForestDavis16_gamma((Int1Exit1P,Ano2)) + 1591.0 ForestDavis16_gamma((Int1Int3P,Ano2)) + 955.0 ForestDavis16_gamma((Int1Org5P,Ano2)) + 1009.0 ForestDavis16_gamma((Org1Int3P,Ano2)) 
+ 818.0 ForestDavis16_gamma((Org1Org2P,Ano2)) + 1091.0 ForestDavis16_gamma((Org1Org3P,Ano2)) + 2582.0 ForestDavis16_gamma((Org2Exit1P,Ano2)) + 818.0 ForestDavis16_gamma((Org3Int1P,Ano2)) + 955.0 ForestDavis16_gamma((Org4Int1P,Ano2)) 
+ 1591.0 ForestDavis16_gamma((Org4Org9P,Ano2)) + 1409.0 ForestDavis16_gamma((Org6Exit1P,Ano2)) + 1591.0 ForestDavis16_gamma((Org7Exit1P,Ano2)) + 900.0 ForestDavis16_gamma((Org8Exit1P,Ano2)) + 1091.0 ForestDavis16_gamma((Org9Int2P,Ano2)) 
- 30.0 ForestDavis16_z((Exit1,Ano2)) = 0.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org1Org2P)_:  1.0 ForestDavis16_gamma((Org1Org2P,Ano1)) + 1.0 ForestDavis16_gamma((Org1Org2P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org1Org2P)_:  1.0 ForestDavis16_gamma((Org1Org2P,Ano1)) + 1.0 ForestDavis16_gamma((Org1Org2P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org6Exit1P)_:  1.0 ForestDavis16_gamma((Org6Exit1P,Ano1)) + 1.0 ForestDavis16_gamma((Org6Exit1P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org6Exit1P)_:  1.0 ForestDavis16_gamma((Org6Exit1P,Ano1)) + 1.0 ForestDavis16_gamma((Org6Exit1P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org3Int1P)_:  1.0 ForestDavis16_gamma((Org3Int1P,Ano1)) + 1.0 ForestDavis16_gamma((Org3Int1P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org3Int1P)_:  1.0 ForestDavis16_gamma((Org3Int1P,Ano1)) + 1.0 ForestDavis16_gamma((Org3Int1P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org4Int1P)_:  1.0 ForestDavis16_gamma((Org4Int1P,Ano1)) + 1.0 ForestDavis16_gamma((Org4Int1P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org4Int1P)_:  1.0 ForestDavis16_gamma((Org4Int1P,Ano1)) + 1.0 ForestDavis16_gamma((Org4Int1P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org7Exit1P)_:  1.0 ForestDavis16_gamma((Org7Exit1P,Ano1)) + 1.0 ForestDavis16_gamma((Org7Exit1P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org7Exit1P)_:  1.0 ForestDavis16_gamma((Org7Exit1P,Ano1)) + 1.0 ForestDavis16_gamma((Org7Exit1P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org2Exit1P)_:  1.0 ForestDavis16_gamma((Org2Exit1P,Ano1)) + 1.0 ForestDavis16_gamma((Org2Exit1P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org2Exit1P)_:  1.0 ForestDavis16_gamma((Org2Exit1P,Ano1)) + 1.0 ForestDavis16_gamma((Org2Exit1P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org1Int3P)_:  1.0 ForestDavis16_gamma((Org1Int3P,Ano1)) + 1.0 ForestDavis16_gamma((Org1Int3P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org1Int3P)_:  1.0 ForestDavis16_gamma((Org1Int3P,Ano1)) + 1.0 ForestDavis16_gamma((Org1Int3P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Int1Exit1P)_:  1.0 ForestDavis16_gamma((Int1Exit1P,Ano1)) + 1.0 ForestDavis16_gamma((Int1Exit1P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Int1Exit1P)_:  1.0 ForestDavis16_gamma((Int1Exit1P,Ano1)) + 1.0 ForestDavis16_gamma((Int1Exit1P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org1Org3P)_:  1.0 ForestDavis16_gamma((Org1Org3P,Ano1)) + 1.0 ForestDavis16_gamma((Org1Org3P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org1Org3P)_:  1.0 ForestDavis16_gamma((Org1Org3P,Ano1)) + 1.0 ForestDavis16_gamma((Org1Org3P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org4Org9P)_:  1.0 ForestDavis16_gamma((Org4Org9P,Ano1)) + 1.0 ForestDavis16_gamma((Org4Org9P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org4Org9P)_:  1.0 ForestDavis16_gamma((Org4Org9P,Ano1)) + 1.0 ForestDavis16_gamma((Org4Org9P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Int1Org5P)_:  1.0 ForestDavis16_gamma((Int1Org5P,Ano1)) + 1.0 ForestDavis16_gamma((Int1Org5P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Int1Org5P)_:  1.0 ForestDavis16_gamma((Int1Org5P,Ano1)) + 1.0 ForestDavis16_gamma((Int1Org5P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org8Exit1P)_:  1.0 ForestDavis16_gamma((Org8Exit1P,Ano1)) + 1.0 ForestDavis16_gamma((Org8Exit1P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org8Exit1P)_:  1.0 ForestDavis16_gamma((Org8Exit1P,Ano1)) + 1.0 ForestDavis16_gamma((Org8Exit1P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Org9Int2P)_:  1.0 ForestDavis16_gamma((Org9Int2P,Ano1)) + 1.0 ForestDavis16_gamma((Org9Int2P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Org9Int2P)_:  1.0 ForestDavis16_gamma((Org9Int2P,Ano1)) + 1.0 ForestDavis16_gamma((Org9Int2P,Ano2)) <= 1.0

ForestDavis16_c_l_EnforceOnePotentialRoad(Int1Int3P)_:  1.0 ForestDavis16_gamma((Int1Int3P,Ano1)) + 1.0 ForestDavis16_gamma((Int1Int3P,Ano2)) >= 0.0

ForestDavis16_c_u_EnforceOnePotentialRoad(Int1Int3P)_:  1.0 ForestDavis16_gamma((Int1Int3P,Ano1)) + 1.0 ForestDavis16_gamma((Int1Int3P,Ano2)) <= 1.0

c_e_ONE_VAR_CONSTANT: ONE_VAR_CONSTANT = 1.0

\ End constraint block for scenario ForestDavis16

bounds

\ Begin variable bounds block for master
     -inf <=  MASTER_Leaf1_AnoProfit(Ano2)  <= +inf
     -inf <=  MASTER_EXPECTED_COST_RootNode  <= +inf
    0 <=  MASTER_RootNode_delta((TrackEighteen,Ano1))  <= 1 
     -inf <=  MASTER_EXPECTED_COST_Leaf4  <= +inf
     -inf <=  MASTER_Leaf3_AnoProfit(Ano2)  <= +inf
     -inf <=  MASTER_EXPECTED_COST_Leaf2  <= +inf
    0 <=  MASTER_RootNode_f((Int1Org5P,Ano1))  <= +inf
     -inf <=  MASTER_EXPECTED_COST_Leaf1  <= +inf
    0 <=  MASTER_RootNode_z((Exit1,Ano1))  <= +inf
     -inf <=  MASTER_EXPECTED_COST_Leaf3  <= +inf
     -inf <=  MASTER_Leaf4_AnoProfit(Ano2)  <= +inf
    0 <=  MASTER_RootNode_gamma((Org1Org3P,Ano1))  <= 1 
     -inf <=  MASTER_RootNode_AnoProfit(Ano1)  <= +inf
     -inf <=  MASTER_Leaf2_AnoProfit(Ano2)  <= +inf
\ End variable bounds block for master

\ Begin variable bounds block for scenario ForestDavis8
    0 <=  ForestDavis8_delta((TrackEleven,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackFour,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackSixteen,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackOne,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwentyOne,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackFourteen,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTen,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackSeven,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwentyThree,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackEight,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackThree,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackThirteen,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackSix,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackNineteen,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackEleven,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackFive,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwenty,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackFourteen,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwo,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwelve,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackSixteen,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackNine,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwentyFive,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackThirteen,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwentyTwo,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwentyThree,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackNineteen,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackFive,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackEight,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackSix,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwo,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackFifteen,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackEighteen,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwentyFour,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackNine,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwenty,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwentyFive,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackSeventeen,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackEighteen,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwelve,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwentyOne,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackOne,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwentyTwo,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackTen,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackFour,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackTwentyFour,Ano1))  <= 1 
    0 <=  ForestDavis8_delta((TrackFifteen,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackThree,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackSeven,Ano2))  <= 1 
    0 <=  ForestDavis8_delta((TrackSeventeen,Ano2))  <= 1 
    0 <=  ForestDavis8_f((Org8Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org1Org2P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org7Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org7Int2E,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org4Org9P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Int1Int2E,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Int1Org5P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org1Org2P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org1Org3P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org3Int1P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org2Int3E,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Int3Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Int3Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org6Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Int1Int2E,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org8Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org2Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org1Int3P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org7Int2E,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Int2Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org4Int1P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org1Org3P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Int1Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Int1Int3P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org2Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org5Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org9Int2P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Int2Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org1Int3P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Int1Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org4Org9P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org4Int1P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org6Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis8_f((Org7Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org3Int1P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Int1Int3P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Int1Org5P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org9Int2P,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org2Int3E,Ano1))  <= +inf
    0 <=  ForestDavis8_f((Org5Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis8_z((Exit1,Ano1))  <= +inf
    0 <=  ForestDavis8_z((Exit1,Ano2))  <= +inf
    0 <=  ForestDavis8_gamma((Org8Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org1Org2P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org7Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org4Org9P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Int1Org5P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org1Org2P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Org1Org3P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org3Int1P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org6Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Org8Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Org2Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org1Int3P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Org4Int1P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org1Org3P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Int1Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Int1Int3P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org2Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Org9Int2P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org1Int3P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Int1Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Org4Org9P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Org4Int1P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Org6Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis8_gamma((Org7Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Org3Int1P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Int1Int3P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Int1Org5P,Ano1))  <= 1 
    0 <=  ForestDavis8_gamma((Org9Int2P,Ano1))  <= 1 
     -inf <=  ForestDavis8_AnoProfit(Ano1)  <= +inf
     -inf <=  ForestDavis8_AnoProfit(Ano2)  <= +inf
\ End variable bounds block for scenario ForestDavis8

\ Begin variable bounds block for scenario ForestDavis12
    0 <=  ForestDavis12_delta((TrackEleven,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackFour,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackSixteen,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackOne,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwentyOne,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackFourteen,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTen,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackSeven,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwentyThree,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackEight,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackThree,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackThirteen,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackSix,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackNineteen,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackEleven,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackFive,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwenty,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackFourteen,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwo,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwelve,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackSixteen,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackNine,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwentyFive,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackThirteen,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwentyTwo,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwentyThree,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackNineteen,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackFive,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackEight,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackSix,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwo,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackFifteen,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackEighteen,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwentyFour,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackNine,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwenty,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwentyFive,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackSeventeen,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackEighteen,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwelve,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwentyOne,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackOne,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwentyTwo,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackTen,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackFour,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackTwentyFour,Ano1))  <= 1 
    0 <=  ForestDavis12_delta((TrackFifteen,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackThree,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackSeven,Ano2))  <= 1 
    0 <=  ForestDavis12_delta((TrackSeventeen,Ano2))  <= 1 
    0 <=  ForestDavis12_f((Org8Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org1Org2P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org7Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org7Int2E,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org4Org9P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Int1Int2E,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Int1Org5P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org1Org2P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org1Org3P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org3Int1P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org2Int3E,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Int3Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Int3Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org6Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Int1Int2E,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org8Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org2Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org1Int3P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org7Int2E,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Int2Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org4Int1P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org1Org3P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Int1Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Int1Int3P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org2Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org5Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org9Int2P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Int2Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org1Int3P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Int1Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org4Org9P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org4Int1P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org6Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis12_f((Org7Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org3Int1P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Int1Int3P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Int1Org5P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org9Int2P,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org2Int3E,Ano1))  <= +inf
    0 <=  ForestDavis12_f((Org5Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis12_z((Exit1,Ano1))  <= +inf
    0 <=  ForestDavis12_z((Exit1,Ano2))  <= +inf
    0 <=  ForestDavis12_gamma((Org8Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org1Org2P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org7Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org4Org9P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Int1Org5P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org1Org2P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Org1Org3P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org3Int1P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org6Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Org8Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Org2Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org1Int3P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Org4Int1P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org1Org3P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Int1Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Int1Int3P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org2Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Org9Int2P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org1Int3P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Int1Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Org4Org9P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Org4Int1P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Org6Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis12_gamma((Org7Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Org3Int1P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Int1Int3P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Int1Org5P,Ano1))  <= 1 
    0 <=  ForestDavis12_gamma((Org9Int2P,Ano1))  <= 1 
     -inf <=  ForestDavis12_AnoProfit(Ano1)  <= +inf
     -inf <=  ForestDavis12_AnoProfit(Ano2)  <= +inf
\ End variable bounds block for scenario ForestDavis12

\ Begin variable bounds block for scenario ForestDavis4
    0 <=  ForestDavis4_delta((TrackEleven,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackFour,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackSixteen,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackOne,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwentyOne,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackFourteen,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTen,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackSeven,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwentyThree,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackEight,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackThree,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackThirteen,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackSix,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackNineteen,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackEleven,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackFive,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwenty,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackFourteen,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwo,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwelve,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackSixteen,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackNine,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwentyFive,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackThirteen,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwentyTwo,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwentyThree,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackNineteen,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackFive,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackEight,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackSix,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwo,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackFifteen,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackEighteen,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwentyFour,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackNine,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwenty,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwentyFive,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackSeventeen,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackEighteen,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwelve,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwentyOne,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackOne,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwentyTwo,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackTen,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackFour,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackTwentyFour,Ano1))  <= 1 
    0 <=  ForestDavis4_delta((TrackFifteen,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackThree,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackSeven,Ano2))  <= 1 
    0 <=  ForestDavis4_delta((TrackSeventeen,Ano2))  <= 1 
    0 <=  ForestDavis4_f((Org8Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org1Org2P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org7Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org7Int2E,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org4Org9P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Int1Int2E,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Int1Org5P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org1Org2P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org1Org3P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org3Int1P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org2Int3E,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Int3Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Int3Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org6Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Int1Int2E,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org8Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org2Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org1Int3P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org7Int2E,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Int2Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org4Int1P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org1Org3P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Int1Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Int1Int3P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org2Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org5Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org9Int2P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Int2Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org1Int3P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Int1Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org4Org9P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org4Int1P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org6Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis4_f((Org7Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org3Int1P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Int1Int3P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Int1Org5P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org9Int2P,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org2Int3E,Ano1))  <= +inf
    0 <=  ForestDavis4_f((Org5Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis4_z((Exit1,Ano1))  <= +inf
    0 <=  ForestDavis4_z((Exit1,Ano2))  <= +inf
    0 <=  ForestDavis4_gamma((Org8Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org1Org2P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org7Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org4Org9P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Int1Org5P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org1Org2P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Org1Org3P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org3Int1P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org6Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Org8Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Org2Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org1Int3P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Org4Int1P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org1Org3P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Int1Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Int1Int3P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org2Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Org9Int2P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org1Int3P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Int1Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Org4Org9P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Org4Int1P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Org6Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis4_gamma((Org7Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Org3Int1P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Int1Int3P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Int1Org5P,Ano1))  <= 1 
    0 <=  ForestDavis4_gamma((Org9Int2P,Ano1))  <= 1 
     -inf <=  ForestDavis4_AnoProfit(Ano1)  <= +inf
     -inf <=  ForestDavis4_AnoProfit(Ano2)  <= +inf
\ End variable bounds block for scenario ForestDavis4

\ Begin variable bounds block for scenario ForestDavis16
    0 <=  ForestDavis16_delta((TrackEleven,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackFour,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackSixteen,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackOne,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwentyOne,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackFourteen,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTen,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackSeven,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwentyThree,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackEight,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackThree,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackThirteen,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackSix,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackNineteen,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackEleven,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackFive,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwenty,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackFourteen,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwo,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwelve,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackSixteen,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackNine,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwentyFive,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackThirteen,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwentyTwo,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwentyThree,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackNineteen,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackFive,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackEight,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackSix,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwo,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackFifteen,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackEighteen,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwentyFour,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackNine,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwenty,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwentyFive,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackSeventeen,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackEighteen,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwelve,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwentyOne,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackOne,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwentyTwo,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackTen,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackFour,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackTwentyFour,Ano1))  <= 1 
    0 <=  ForestDavis16_delta((TrackFifteen,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackThree,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackSeven,Ano2))  <= 1 
    0 <=  ForestDavis16_delta((TrackSeventeen,Ano2))  <= 1 
    0 <=  ForestDavis16_f((Org8Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org1Org2P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org7Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org7Int2E,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org4Org9P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Int1Int2E,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Int1Org5P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org1Org2P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org1Org3P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org3Int1P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org2Int3E,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Int3Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Int3Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org6Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Int1Int2E,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org8Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org2Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org1Int3P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org7Int2E,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Int2Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org4Int1P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org1Org3P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Int1Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Int1Int3P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org2Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org5Exit1E,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org9Int2P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Int2Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org1Int3P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Int1Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org4Org9P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org4Int1P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org6Exit1P,Ano2))  <= +inf
    0 <=  ForestDavis16_f((Org7Exit1P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org3Int1P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Int1Int3P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Int1Org5P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org9Int2P,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org2Int3E,Ano1))  <= +inf
    0 <=  ForestDavis16_f((Org5Exit1E,Ano2))  <= +inf
    0 <=  ForestDavis16_z((Exit1,Ano1))  <= +inf
    0 <=  ForestDavis16_z((Exit1,Ano2))  <= +inf
    0 <=  ForestDavis16_gamma((Org8Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org1Org2P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org7Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org4Org9P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Int1Org5P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org1Org2P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Org1Org3P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org3Int1P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org6Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Org8Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Org2Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org1Int3P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Org4Int1P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org1Org3P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Int1Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Int1Int3P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org2Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Org9Int2P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org1Int3P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Int1Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Org4Org9P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Org4Int1P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Org6Exit1P,Ano2))  <= 1 
    0 <=  ForestDavis16_gamma((Org7Exit1P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Org3Int1P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Int1Int3P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Int1Org5P,Ano1))  <= 1 
    0 <=  ForestDavis16_gamma((Org9Int2P,Ano1))  <= 1 
     -inf <=  ForestDavis16_AnoProfit(Ano1)  <= +inf
     -inf <=  ForestDavis16_AnoProfit(Ano2)  <= +inf
\ End variable bounds block for scenario ForestDavis16

binary

\ Begin binary variable block for master
    MASTER_RootNode_delta((TrackEighteen,Ano1))
    MASTER_RootNode_gamma((Org1Org3P,Ano1))
\ End binary variable block for master

\ Begin binary variable block for scenario ForestDavis8
    ForestDavis8_delta((TrackEleven,Ano2))
    ForestDavis8_delta((TrackFour,Ano2))
    ForestDavis8_delta((TrackSixteen,Ano2))
    ForestDavis8_delta((TrackOne,Ano1))
    ForestDavis8_delta((TrackTwentyOne,Ano2))
    ForestDavis8_delta((TrackFourteen,Ano1))
    ForestDavis8_delta((TrackTen,Ano2))
    ForestDavis8_delta((TrackSeven,Ano1))
    ForestDavis8_delta((TrackTwentyThree,Ano1))
    ForestDavis8_delta((TrackEight,Ano1))
    ForestDavis8_delta((TrackThree,Ano1))
    ForestDavis8_delta((TrackThirteen,Ano2))
    ForestDavis8_delta((TrackSix,Ano2))
    ForestDavis8_delta((TrackNineteen,Ano1))
    ForestDavis8_delta((TrackEleven,Ano1))
    ForestDavis8_delta((TrackFive,Ano1))
    ForestDavis8_delta((TrackTwenty,Ano2))
    ForestDavis8_delta((TrackFourteen,Ano2))
    ForestDavis8_delta((TrackTwo,Ano2))
    ForestDavis8_delta((TrackTwelve,Ano2))
    ForestDavis8_delta((TrackSixteen,Ano1))
    ForestDavis8_delta((TrackNine,Ano1))
    ForestDavis8_delta((TrackTwentyFive,Ano2))
    ForestDavis8_delta((TrackThirteen,Ano1))
    ForestDavis8_delta((TrackTwentyTwo,Ano1))
    ForestDavis8_delta((TrackTwentyThree,Ano2))
    ForestDavis8_delta((TrackNineteen,Ano2))
    ForestDavis8_delta((TrackFive,Ano2))
    ForestDavis8_delta((TrackEight,Ano2))
    ForestDavis8_delta((TrackSix,Ano1))
    ForestDavis8_delta((TrackTwo,Ano1))
    ForestDavis8_delta((TrackFifteen,Ano1))
    ForestDavis8_delta((TrackEighteen,Ano1))
    ForestDavis8_delta((TrackTwentyFour,Ano2))
    ForestDavis8_delta((TrackNine,Ano2))
    ForestDavis8_delta((TrackTwenty,Ano1))
    ForestDavis8_delta((TrackTwentyFive,Ano1))
    ForestDavis8_delta((TrackSeventeen,Ano1))
    ForestDavis8_delta((TrackEighteen,Ano2))
    ForestDavis8_delta((TrackTwelve,Ano1))
    ForestDavis8_delta((TrackTwentyOne,Ano1))
    ForestDavis8_delta((TrackOne,Ano2))
    ForestDavis8_delta((TrackTwentyTwo,Ano2))
    ForestDavis8_delta((TrackTen,Ano1))
    ForestDavis8_delta((TrackFour,Ano1))
    ForestDavis8_delta((TrackTwentyFour,Ano1))
    ForestDavis8_delta((TrackFifteen,Ano2))
    ForestDavis8_delta((TrackThree,Ano2))
    ForestDavis8_delta((TrackSeven,Ano2))
    ForestDavis8_delta((TrackSeventeen,Ano2))
    ForestDavis8_gamma((Org8Exit1P,Ano2))
    ForestDavis8_gamma((Org1Org2P,Ano2))
    ForestDavis8_gamma((Org7Exit1P,Ano2))
    ForestDavis8_gamma((Org4Org9P,Ano2))
    ForestDavis8_gamma((Int1Org5P,Ano2))
    ForestDavis8_gamma((Org1Org2P,Ano1))
    ForestDavis8_gamma((Org1Org3P,Ano2))
    ForestDavis8_gamma((Org3Int1P,Ano2))
    ForestDavis8_gamma((Org6Exit1P,Ano1))
    ForestDavis8_gamma((Org8Exit1P,Ano1))
    ForestDavis8_gamma((Org2Exit1P,Ano2))
    ForestDavis8_gamma((Org1Int3P,Ano1))
    ForestDavis8_gamma((Org4Int1P,Ano2))
    ForestDavis8_gamma((Org1Org3P,Ano1))
    ForestDavis8_gamma((Int1Exit1P,Ano2))
    ForestDavis8_gamma((Int1Int3P,Ano2))
    ForestDavis8_gamma((Org2Exit1P,Ano1))
    ForestDavis8_gamma((Org9Int2P,Ano2))
    ForestDavis8_gamma((Org1Int3P,Ano2))
    ForestDavis8_gamma((Int1Exit1P,Ano1))
    ForestDavis8_gamma((Org4Org9P,Ano1))
    ForestDavis8_gamma((Org4Int1P,Ano1))
    ForestDavis8_gamma((Org6Exit1P,Ano2))
    ForestDavis8_gamma((Org7Exit1P,Ano1))
    ForestDavis8_gamma((Org3Int1P,Ano1))
    ForestDavis8_gamma((Int1Int3P,Ano1))
    ForestDavis8_gamma((Int1Org5P,Ano1))
    ForestDavis8_gamma((Org9Int2P,Ano1))
\ End integer binary block for scenario ForestDavis8

\ Begin binary variable block for scenario ForestDavis12
    ForestDavis12_delta((TrackEleven,Ano2))
    ForestDavis12_delta((TrackFour,Ano2))
    ForestDavis12_delta((TrackSixteen,Ano2))
    ForestDavis12_delta((TrackOne,Ano1))
    ForestDavis12_delta((TrackTwentyOne,Ano2))
    ForestDavis12_delta((TrackFourteen,Ano1))
    ForestDavis12_delta((TrackTen,Ano2))
    ForestDavis12_delta((TrackSeven,Ano1))
    ForestDavis12_delta((TrackTwentyThree,Ano1))
    ForestDavis12_delta((TrackEight,Ano1))
    ForestDavis12_delta((TrackThree,Ano1))
    ForestDavis12_delta((TrackThirteen,Ano2))
    ForestDavis12_delta((TrackSix,Ano2))
    ForestDavis12_delta((TrackNineteen,Ano1))
    ForestDavis12_delta((TrackEleven,Ano1))
    ForestDavis12_delta((TrackFive,Ano1))
    ForestDavis12_delta((TrackTwenty,Ano2))
    ForestDavis12_delta((TrackFourteen,Ano2))
    ForestDavis12_delta((TrackTwo,Ano2))
    ForestDavis12_delta((TrackTwelve,Ano2))
    ForestDavis12_delta((TrackSixteen,Ano1))
    ForestDavis12_delta((TrackNine,Ano1))
    ForestDavis12_delta((TrackTwentyFive,Ano2))
    ForestDavis12_delta((TrackThirteen,Ano1))
    ForestDavis12_delta((TrackTwentyTwo,Ano1))
    ForestDavis12_delta((TrackTwentyThree,Ano2))
    ForestDavis12_delta((TrackNineteen,Ano2))
    ForestDavis12_delta((TrackFive,Ano2))
    ForestDavis12_delta((TrackEight,Ano2))
    ForestDavis12_delta((TrackSix,Ano1))
    ForestDavis12_delta((TrackTwo,Ano1))
    ForestDavis12_delta((TrackFifteen,Ano1))
    ForestDavis12_delta((TrackEighteen,Ano1))
    ForestDavis12_delta((TrackTwentyFour,Ano2))
    ForestDavis12_delta((TrackNine,Ano2))
    ForestDavis12_delta((TrackTwenty,Ano1))
    ForestDavis12_delta((TrackTwentyFive,Ano1))
    ForestDavis12_delta((TrackSeventeen,Ano1))
    ForestDavis12_delta((TrackEighteen,Ano2))
    ForestDavis12_delta((TrackTwelve,Ano1))
    ForestDavis12_delta((TrackTwentyOne,Ano1))
    ForestDavis12_delta((TrackOne,Ano2))
    ForestDavis12_delta((TrackTwentyTwo,Ano2))
    ForestDavis12_delta((TrackTen,Ano1))
    ForestDavis12_delta((TrackFour,Ano1))
    ForestDavis12_delta((TrackTwentyFour,Ano1))
    ForestDavis12_delta((TrackFifteen,Ano2))
    ForestDavis12_delta((TrackThree,Ano2))
    ForestDavis12_delta((TrackSeven,Ano2))
    ForestDavis12_delta((TrackSeventeen,Ano2))
    ForestDavis12_gamma((Org8Exit1P,Ano2))
    ForestDavis12_gamma((Org1Org2P,Ano2))
    ForestDavis12_gamma((Org7Exit1P,Ano2))
    ForestDavis12_gamma((Org4Org9P,Ano2))
    ForestDavis12_gamma((Int1Org5P,Ano2))
    ForestDavis12_gamma((Org1Org2P,Ano1))
    ForestDavis12_gamma((Org1Org3P,Ano2))
    ForestDavis12_gamma((Org3Int1P,Ano2))
    ForestDavis12_gamma((Org6Exit1P,Ano1))
    ForestDavis12_gamma((Org8Exit1P,Ano1))
    ForestDavis12_gamma((Org2Exit1P,Ano2))
    ForestDavis12_gamma((Org1Int3P,Ano1))
    ForestDavis12_gamma((Org4Int1P,Ano2))
    ForestDavis12_gamma((Org1Org3P,Ano1))
    ForestDavis12_gamma((Int1Exit1P,Ano2))
    ForestDavis12_gamma((Int1Int3P,Ano2))
    ForestDavis12_gamma((Org2Exit1P,Ano1))
    ForestDavis12_gamma((Org9Int2P,Ano2))
    ForestDavis12_gamma((Org1Int3P,Ano2))
    ForestDavis12_gamma((Int1Exit1P,Ano1))
    ForestDavis12_gamma((Org4Org9P,Ano1))
    ForestDavis12_gamma((Org4Int1P,Ano1))
    ForestDavis12_gamma((Org6Exit1P,Ano2))
    ForestDavis12_gamma((Org7Exit1P,Ano1))
    ForestDavis12_gamma((Org3Int1P,Ano1))
    ForestDavis12_gamma((Int1Int3P,Ano1))
    ForestDavis12_gamma((Int1Org5P,Ano1))
    ForestDavis12_gamma((Org9Int2P,Ano1))
\ End integer binary block for scenario ForestDavis12

\ Begin binary variable block for scenario ForestDavis4
    ForestDavis4_delta((TrackEleven,Ano2))
    ForestDavis4_delta((TrackFour,Ano2))
    ForestDavis4_delta((TrackSixteen,Ano2))
    ForestDavis4_delta((TrackOne,Ano1))
    ForestDavis4_delta((TrackTwentyOne,Ano2))
    ForestDavis4_delta((TrackFourteen,Ano1))
    ForestDavis4_delta((TrackTen,Ano2))
    ForestDavis4_delta((TrackSeven,Ano1))
    ForestDavis4_delta((TrackTwentyThree,Ano1))
    ForestDavis4_delta((TrackEight,Ano1))
    ForestDavis4_delta((TrackThree,Ano1))
    ForestDavis4_delta((TrackThirteen,Ano2))
    ForestDavis4_delta((TrackSix,Ano2))
    ForestDavis4_delta((TrackNineteen,Ano1))
    ForestDavis4_delta((TrackEleven,Ano1))
    ForestDavis4_delta((TrackFive,Ano1))
    ForestDavis4_delta((TrackTwenty,Ano2))
    ForestDavis4_delta((TrackFourteen,Ano2))
    ForestDavis4_delta((TrackTwo,Ano2))
    ForestDavis4_delta((TrackTwelve,Ano2))
    ForestDavis4_delta((TrackSixteen,Ano1))
    ForestDavis4_delta((TrackNine,Ano1))
    ForestDavis4_delta((TrackTwentyFive,Ano2))
    ForestDavis4_delta((TrackThirteen,Ano1))
    ForestDavis4_delta((TrackTwentyTwo,Ano1))
    ForestDavis4_delta((TrackTwentyThree,Ano2))
    ForestDavis4_delta((TrackNineteen,Ano2))
    ForestDavis4_delta((TrackFive,Ano2))
    ForestDavis4_delta((TrackEight,Ano2))
    ForestDavis4_delta((TrackSix,Ano1))
    ForestDavis4_delta((TrackTwo,Ano1))
    ForestDavis4_delta((TrackFifteen,Ano1))
    ForestDavis4_delta((TrackEighteen,Ano1))
    ForestDavis4_delta((TrackTwentyFour,Ano2))
    ForestDavis4_delta((TrackNine,Ano2))
    ForestDavis4_delta((TrackTwenty,Ano1))
    ForestDavis4_delta((TrackTwentyFive,Ano1))
    ForestDavis4_delta((TrackSeventeen,Ano1))
    ForestDavis4_delta((TrackEighteen,Ano2))
    ForestDavis4_delta((TrackTwelve,Ano1))
    ForestDavis4_delta((TrackTwentyOne,Ano1))
    ForestDavis4_delta((TrackOne,Ano2))
    ForestDavis4_delta((TrackTwentyTwo,Ano2))
    ForestDavis4_delta((TrackTen,Ano1))
    ForestDavis4_delta((TrackFour,Ano1))
    ForestDavis4_delta((TrackTwentyFour,Ano1))
    ForestDavis4_delta((TrackFifteen,Ano2))
    ForestDavis4_delta((TrackThree,Ano2))
    ForestDavis4_delta((TrackSeven,Ano2))
    ForestDavis4_delta((TrackSeventeen,Ano2))
    ForestDavis4_gamma((Org8Exit1P,Ano2))
    ForestDavis4_gamma((Org1Org2P,Ano2))
    ForestDavis4_gamma((Org7Exit1P,Ano2))
    ForestDavis4_gamma((Org4Org9P,Ano2))
    ForestDavis4_gamma((Int1Org5P,Ano2))
    ForestDavis4_gamma((Org1Org2P,Ano1))
    ForestDavis4_gamma((Org1Org3P,Ano2))
    ForestDavis4_gamma((Org3Int1P,Ano2))
    ForestDavis4_gamma((Org6Exit1P,Ano1))
    ForestDavis4_gamma((Org8Exit1P,Ano1))
    ForestDavis4_gamma((Org2Exit1P,Ano2))
    ForestDavis4_gamma((Org1Int3P,Ano1))
    ForestDavis4_gamma((Org4Int1P,Ano2))
    ForestDavis4_gamma((Org1Org3P,Ano1))
    ForestDavis4_gamma((Int1Exit1P,Ano2))
    ForestDavis4_gamma((Int1Int3P,Ano2))
    ForestDavis4_gamma((Org2Exit1P,Ano1))
    ForestDavis4_gamma((Org9Int2P,Ano2))
    ForestDavis4_gamma((Org1Int3P,Ano2))
    ForestDavis4_gamma((Int1Exit1P,Ano1))
    ForestDavis4_gamma((Org4Org9P,Ano1))
    ForestDavis4_gamma((Org4Int1P,Ano1))
    ForestDavis4_gamma((Org6Exit1P,Ano2))
    ForestDavis4_gamma((Org7Exit1P,Ano1))
    ForestDavis4_gamma((Org3Int1P,Ano1))
    ForestDavis4_gamma((Int1Int3P,Ano1))
    ForestDavis4_gamma((Int1Org5P,Ano1))
    ForestDavis4_gamma((Org9Int2P,Ano1))
\ End integer binary block for scenario ForestDavis4

\ Begin binary variable block for scenario ForestDavis16
    ForestDavis16_delta((TrackEleven,Ano2))
    ForestDavis16_delta((TrackFour,Ano2))
    ForestDavis16_delta((TrackSixteen,Ano2))
    ForestDavis16_delta((TrackOne,Ano1))
    ForestDavis16_delta((TrackTwentyOne,Ano2))
    ForestDavis16_delta((TrackFourteen,Ano1))
    ForestDavis16_delta((TrackTen,Ano2))
    ForestDavis16_delta((TrackSeven,Ano1))
    ForestDavis16_delta((TrackTwentyThree,Ano1))
    ForestDavis16_delta((TrackEight,Ano1))
    ForestDavis16_delta((TrackThree,Ano1))
    ForestDavis16_delta((TrackThirteen,Ano2))
    ForestDavis16_delta((TrackSix,Ano2))
    ForestDavis16_delta((TrackNineteen,Ano1))
    ForestDavis16_delta((TrackEleven,Ano1))
    ForestDavis16_delta((TrackFive,Ano1))
    ForestDavis16_delta((TrackTwenty,Ano2))
    ForestDavis16_delta((TrackFourteen,Ano2))
    ForestDavis16_delta((TrackTwo,Ano2))
    ForestDavis16_delta((TrackTwelve,Ano2))
    ForestDavis16_delta((TrackSixteen,Ano1))
    ForestDavis16_delta((TrackNine,Ano1))
    ForestDavis16_delta((TrackTwentyFive,Ano2))
    ForestDavis16_delta((TrackThirteen,Ano1))
    ForestDavis16_delta((TrackTwentyTwo,Ano1))
    ForestDavis16_delta((TrackTwentyThree,Ano2))
    ForestDavis16_delta((TrackNineteen,Ano2))
    ForestDavis16_delta((TrackFive,Ano2))
    ForestDavis16_delta((TrackEight,Ano2))
    ForestDavis16_delta((TrackSix,Ano1))
    ForestDavis16_delta((TrackTwo,Ano1))
    ForestDavis16_delta((TrackFifteen,Ano1))
    ForestDavis16_delta((TrackEighteen,Ano1))
    ForestDavis16_delta((TrackTwentyFour,Ano2))
    ForestDavis16_delta((TrackNine,Ano2))
    ForestDavis16_delta((TrackTwenty,Ano1))
    ForestDavis16_delta((TrackTwentyFive,Ano1))
    ForestDavis16_delta((TrackSeventeen,Ano1))
    ForestDavis16_delta((TrackEighteen,Ano2))
    ForestDavis16_delta((TrackTwelve,Ano1))
    ForestDavis16_delta((TrackTwentyOne,Ano1))
    ForestDavis16_delta((TrackOne,Ano2))
    ForestDavis16_delta((TrackTwentyTwo,Ano2))
    ForestDavis16_delta((TrackTen,Ano1))
    ForestDavis16_delta((TrackFour,Ano1))
    ForestDavis16_delta((TrackTwentyFour,Ano1))
    ForestDavis16_delta((TrackFifteen,Ano2))
    ForestDavis16_delta((TrackThree,Ano2))
    ForestDavis16_delta((TrackSeven,Ano2))
    ForestDavis16_delta((TrackSeventeen,Ano2))
    ForestDavis16_gamma((Org8Exit1P,Ano2))
    ForestDavis16_gamma((Org1Org2P,Ano2))
    ForestDavis16_gamma((Org7Exit1P,Ano2))
    ForestDavis16_gamma((Org4Org9P,Ano2))
    ForestDavis16_gamma((Int1Org5P,Ano2))
    ForestDavis16_gamma((Org1Org2P,Ano1))
    ForestDavis16_gamma((Org1Org3P,Ano2))
    ForestDavis16_gamma((Org3Int1P,Ano2))
    ForestDavis16_gamma((Org6Exit1P,Ano1))
    ForestDavis16_gamma((Org8Exit1P,Ano1))
    ForestDavis16_gamma((Org2Exit1P,Ano2))
    ForestDavis16_gamma((Org1Int3P,Ano1))
    ForestDavis16_gamma((Org4Int1P,Ano2))
    ForestDavis16_gamma((Org1Org3P,Ano1))
    ForestDavis16_gamma((Int1Exit1P,Ano2))
    ForestDavis16_gamma((Int1Int3P,Ano2))
    ForestDavis16_gamma((Org2Exit1P,Ano1))
    ForestDavis16_gamma((Org9Int2P,Ano2))
    ForestDavis16_gamma((Org1Int3P,Ano2))
    ForestDavis16_gamma((Int1Exit1P,Ano1))
    ForestDavis16_gamma((Org4Org9P,Ano1))
    ForestDavis16_gamma((Org4Int1P,Ano1))
    ForestDavis16_gamma((Org6Exit1P,Ano2))
    ForestDavis16_gamma((Org7Exit1P,Ano1))
    ForestDavis16_gamma((Org3Int1P,Ano1))
    ForestDavis16_gamma((Int1Int3P,Ano1))
    ForestDavis16_gamma((Int1Org5P,Ano1))
    ForestDavis16_gamma((Org9Int2P,Ano1))
\ End integer binary block for scenario ForestDavis16

end
