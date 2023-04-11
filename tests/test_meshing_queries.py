from ansys.fluent.core import examples

import_filename = examples.download_file(
    "elbow.cas.h5", "pyfluent/examples/DOE-ML-Mixing-Elbow"
)


def test_meshing_queries(new_mesh_session):
    meshing_session = new_mesh_session
    meshing_session.tui.file.read_case(import_filename)

    assert meshing_session.meshing_queries.GetFaceZoneAtLocation([1.4, 1.4, 1.4]) == 34

    assert meshing_session.meshing_queries.GetZonesOfType("velocity-inlet") == [30, 31]

    assert meshing_session.meshing_queries.GetZonesOfGroup("inlet") == [31, 30]

    assert meshing_session.meshing_queries.GetFaceZonesOfFilter("*") == [
        3462,
        34,
        33,
        32,
        31,
        30,
        29,
    ]

    assert meshing_session.meshing_queries.GetCellZonesOfFilter("*") == [3460]

    assert meshing_session.meshing_queries.GetEdgeZonesOfFilter("*") == []

    assert meshing_session.meshing_queries.GetNodeZonesOfFilter("*") == [3625, 3624]

    assert meshing_session.meshing_queries.GetObjectsOfType("mesh") == ["elbow-fluid"]

    assert meshing_session.meshing_queries.GetFaceZoneIdListOfObject("elbow-fluid") == [
        29,
        30,
        31,
        32,
        33,
        34,
    ]

    assert (
        meshing_session.meshing_queries.GetEdgeZoneIdListOfObject("elbow-fluid") == []
    )

    assert meshing_session.meshing_queries.GetCellZoneIdListOfObject("elbow-fluid") == [
        3460
    ]

    assert (
        meshing_session.meshing_queries.GetFaceZonesSharedByRegionsOfType(
            "elbow-fluid", "fluid-fluid"
        )
        == []
    )

    assert meshing_session.meshing_queries.GetFaceZonesOfRegions(
        "elbow-fluid", ["fluid"]
    ) == [34, 33, 32, 31, 30, 29]

    assert meshing_session.meshing_queries.GetFaceZonesOfLabels(
        "elbow-fluid", ["inlet", "outlet", "wall", "internal"]
    ) == [32]

    assert meshing_session.meshing_queries.GetFaceZoneIdListOfLabels(
        "elbow-fluid", ["outlet"]
    ) == [32]

    assert meshing_session.meshing_queries.GetFaceZonesOfObjects(["elbow-fluid"]) == [
        29,
        30,
        31,
        32,
        33,
        34,
    ]

    assert meshing_session.meshing_queries.GetEdgeZonesOfObjects(["elbow-fluid"]) == []

    assert meshing_session.meshing_queries.GetFaceZoneIdListOfRegions(
        "elbow-fluid", ["fluid"]
    ) == [
        34,
        33,
        32,
        31,
        30,
        29,
    ]

    assert meshing_session.meshing_queries.GetPrismCellZones(["inlet", "outlet"]) == []

    assert meshing_session.meshing_queries.GetPrismCellZones("*") == []

    assert meshing_session.meshing_queries.GetTetCellZones(["inlet", "outlet"]) == []

    assert meshing_session.meshing_queries.GetTetCellZones("*") == []

    assert meshing_session.meshing_queries.GetAdjacentCellZones([30]) == [3460]

    assert meshing_session.meshing_queries.GetAdjacentCellZones("*") == [3460]

    assert meshing_session.meshing_queries.GetAdjacentFaceZones([3460]) == [
        29,
        30,
        31,
        32,
        33,
        34,
    ]

    assert meshing_session.meshing_queries.GetAdjacentFaceZones("*") == [
        29,
        30,
        31,
        32,
        33,
        34,
    ]

    assert (
        meshing_session.meshing_queries.GetAdjacentInteriorAndBoundaryFaceZones([30])
        == []
    )

    assert meshing_session.meshing_queries.GetAdjacentInteriorAndBoundaryFaceZones(
        "*"
    ) == [
        29,
        30,
        31,
        32,
        33,
        34,
        3462,
    ]

    assert meshing_session.meshing_queries.GetAdjacentZonesByEdgeConnectivity([30]) == [
        33,
        29,
    ]

    assert meshing_session.meshing_queries.GetAdjacentZonesByEdgeConnectivity("*") == []

    assert meshing_session.meshing_queries.GetAdjacentZonesByNodeConnectivity([30]) == [
        29,
        33,
    ]

    assert meshing_session.meshing_queries.GetAdjacentZonesByNodeConnectivity("*") == []

    assert meshing_session.meshing_queries.GetInteriorZonesConnectedToCellZones(
        [3460]
    ) == [3462]

    assert meshing_session.meshing_queries.GetInteriorZonesConnectedToCellZones(
        "*"
    ) == [3462]

    assert (
        meshing_session.meshing_queries.GetFaceZonesWithZoneSpecificPrismsApplied()
        == []
    )

    assert meshing_session.meshing_queries.GetBaffles([29, 30]) == [30, 29]

    assert meshing_session.meshing_queries.GetEmbeddedBaffles() == []

    assert meshing_session.meshing_queries.GetWrappedZones() == []

    assert meshing_session.meshing_queries.GetUnreferencedEdgeZones() == []

    assert meshing_session.meshing_queries.GetUnreferencedEdgeZones() == []

    assert meshing_session.meshing_queries.GetUnreferencedEdgeZones() == []

    assert meshing_session.meshing_queries.GetUnreferencedEdgeZonesOfFilter("*") == []

    assert meshing_session.meshing_queries.GetUnreferencedFaceZonesOfFilter("*") == []

    assert meshing_session.meshing_queries.GetUnreferencedCellZonesOfFilter("*") == []

    assert (
        meshing_session.meshing_queries.GetUnreferencedEdgeZoneIdListOfPattern("*")
        == []
    )

    assert (
        meshing_session.meshing_queries.GetUnreferencedFaceZoneIdListOfPattern("*")
        == []
    )

    assert (
        meshing_session.meshing_queries.GetUnreferencedCellZoneIdListOfPattern("*")
        == []
    )

    # assert meshing_session.meshing_queries.GetMaxsizeCellZoneByVolume("*") == [3460]
    #
    # assert meshing_session.meshing_queries.GetMaxsizeCellZoneByVolume([3460]) == [3460]
    #
    # assert meshing_session.meshing_queries.GetMaxsizeCellZoneByCount("*") == [3460]
    #
    # assert meshing_session.meshing_queries.GetMaxsizeCellZoneByCount([3460]) == [3460]
    #
    # assert meshing_session.meshing_queries.GetMinsizeFaceZoneByArea("*") == [30]
    #
    # assert meshing_session.meshing_queries.GetMinsizeFaceZoneByArea([29, 30, 31, 32, 33, 34]) == [30]
    #
    # assert meshing_session.meshing_queries.GetMinsizeFaceZoneByCount("*") == [30]
    #
    # assert meshing_session.meshing_queries.GetMinsizeFaceZoneByCount([29, 30, 31, 32, 33, 34]) == [30]

    assert (
        meshing_session.meshing_queries.GetFaceZoneListByMaximumEntityCount(20, True)
        == []
    )

    assert (
        meshing_session.meshing_queries.GetEdgeZoneListByMaximumEntityCount(20, False)
        == []
    )

    assert meshing_session.meshing_queries.GetCellZoneListByMaximumEntityCount(1) == []

    assert meshing_session.meshing_queries.GetFaceZoneListByMaximumZoneArea(100) == [
        33,
        32,
        31,
        30,
    ]

    assert meshing_session.meshing_queries.GetFaceZoneListByMinimumZoneArea(10) == [
        34,
        29,
    ]

    assert meshing_session.meshing_queries.GetZonesWithFreeFaces("*") == []
    assert meshing_session.meshing_queries.GetZonesWithFreeFaces([29, 30, 31, 32]) == []
    assert (
        meshing_session.meshing_queries.GetZonesWithFreeFaces(["inlet", "outlet"]) == []
    )

    assert meshing_session.meshing_queries.GetZonesWithMultiFaces("*") == []
    assert (
        meshing_session.meshing_queries.GetZonesWithMultiFaces([29, 30, 31, 32]) == []
    )
    assert (
        meshing_session.meshing_queries.GetZonesWithMultiFaces(["inlet", "outlet"])
        == []
    )

    assert meshing_session.meshing_queries.GetOverlappingFaceZones("*", 0.1, 0.1) == []

    assert meshing_session.meshing_queries.GetZonesWithMarkedFaces("*") == []
    assert (
        meshing_session.meshing_queries.GetZonesWithMarkedFaces([29, 30, 31, 32]) == []
    )
    assert (
        meshing_session.meshing_queries.GetZonesWithMarkedFaces(["inlet", "outlet"])
        == []
    )

    assert meshing_session.meshing_queries.GetAllObjectNameList() == ["elbow-fluid"]

    assert meshing_session.meshing_queries.GetObjectNameListOfType("mesh") == [
        "elbow-fluid"
    ]

    assert meshing_session.meshing_queries.GetObjectsOfFilter("*") == ["elbow-fluid"]

    assert meshing_session.meshing_queries.GetRegionsOfObject("elbow-fluid") == [
        "fluid"
    ]

    assert meshing_session.meshing_queries.GetRegionNameListOfObject("elbow-fluid") == [
        "fluid"
    ]

    assert (
        meshing_session.meshing_queries.GetRegionVolume("elbow-fluid", "fluid")
        == 152.599422561798
    )

    assert meshing_session.meshing_queries.GetRegionsOfFilter("elbow-fluid", "*") == [
        "fluid"
    ]

    assert meshing_session.meshing_queries.GetRegionNameListOfPattern(
        "elbow-fluid", "*"
    ) == ["fluid"]

    assert meshing_session.meshing_queries.GetRegionsOfFaceZones(
        [29, 30, 31, 32, 33, 34]
    ) == ["fluid"]

    assert meshing_session.meshing_queries.GetRegionNameListOfFaceZones(
        [29, 30, 31, 32, 33, 34]
    ) == ["fluid"]

    assert meshing_session.meshing_queries.ConvertZoneNameSymbolsToIds(["outlet"]) == [
        32
    ]

    assert meshing_session.meshing_queries.ConvertZoneNameStringsToIds(["outlet"]) == [
        32
    ]

    assert meshing_session.meshing_queries.ConvertZoneIdsToNameStrings([29]) == [
        "symmetry-xyplane"
    ]

    assert meshing_session.meshing_queries.ConvertZoneIdsToNameSymbols([31]) == [
        "cold-inlet"
    ]

    assert (
        meshing_session.meshing_queries.ConvertSymbolListToString(["inlet", "outlet"])
        == "inlet outlet "
    )

    assert (
        meshing_session.meshing_queries.CreateStringFromSymbolList(["inlet", "outlet"])
        == "inlet outlet"
    )

    assert meshing_session.meshing_queries.IntegerListSubstract(
        [1, 2, 3, 4], [2, 3]
    ) == [1, 4]

    assert meshing_session.meshing_queries.ListReplace(4, 2, [1, 2, 3]) == [1, 4, 3]

    assert meshing_session.meshing_queries.ListReplace(4.4, 2.2, [1.1, 2.2, 3.3]) == [
        1.1,
        4.4,
        3.3,
    ]

    assert meshing_session.meshing_queries.RemoveElementFromList(2, [1, 2, 3]) == [1, 3]

    assert meshing_session.meshing_queries.RemoveElementFromList(
        2.2, [1.1, 2.2, 3.3]
    ) == [1.1, 3.3]

    assert meshing_session.meshing_queries.ListContains(4, [1, 2, 3]) is False

    assert meshing_session.meshing_queries.ListContains(2.2, [1.1, 2.2, 3.3]) is True
