
import numpy as np
from netCDF4 import Dataset
from scipy.sparse import csr_matrix, spdiags
from scipy.sparse.csgraph import reverse_cuthill_mckee


def load_mesh(name, rsph=None):
    """
    LOAD-MESH: load the NAME.nc MPAS mesh file into a
    local mesh data structure.

    """
    # Authors: Darren Engwirda, Sara Calandrini

    class base: pass

    data = Dataset(name, "r")

    mesh = base()
    mesh.rsph = float(data.sphere_radius)

    if (rsph is not None):
        scal = rsph / mesh.rsph
        mesh.rsph = mesh.rsph * scal
    else:
        scal = 1.0E+00

    mesh.cell = base()
    mesh.cell.size = int(data.dimensions["nCells"].size)
    mesh.cell.xpos = np.array(data.variables["xCell"]) * scal
    mesh.cell.ypos = np.array(data.variables["yCell"]) * scal
    mesh.cell.zpos = np.array(data.variables["zCell"]) * scal
    mesh.cell.xlon = np.array(data.variables["lonCell"])
    mesh.cell.ylat = np.array(data.variables["latCell"])
   #mesh.cell.area = \
   #    np.array(data.variables["areaCell"]) * scal ** 2
    mesh.cell.vert = \
        np.array(data.variables["verticesOnCell"])
    mesh.cell.edge = \
        np.array(data.variables["edgesOnCell"])
    mesh.cell.cell = \
        np.array(data.variables["cellsOnCell"])
    mesh.cell.topo = \
        np.array(data.variables["nEdgesOnCell"])

    mesh.edge = base()
    mesh.edge.size = int(data.dimensions["nEdges"].size)
    mesh.edge.xpos = np.array(data.variables["xEdge"]) * scal
    mesh.edge.ypos = np.array(data.variables["yEdge"]) * scal
    mesh.edge.zpos = np.array(data.variables["zEdge"]) * scal
    mesh.edge.xlon = np.array(data.variables["lonEdge"])
    mesh.edge.ylat = np.array(data.variables["latEdge"])
   #mesh.edge.vlen = np.array(data.variables["dvEdge"]) * scal
   #mesh.edge.clen = np.array(data.variables["dcEdge"]) * scal
    mesh.edge.vert = \
        np.array(data.variables["verticesOnEdge"])
    mesh.edge.wmul = \
        np.array(data.variables["weightsOnEdge"])
    mesh.edge.cell = \
        np.array(data.variables["cellsOnEdge"])
    mesh.edge.edge = \
        np.array(data.variables["edgesOnEdge"])
    mesh.edge.topo = \
        np.array(data.variables["nEdgesOnEdge"])

    mesh.vert = base()
    mesh.vert.size = int(data.dimensions["nVertices"].size)
    mesh.vert.xpos = np.array(data.variables["xVertex"]) * scal
    mesh.vert.ypos = np.array(data.variables["yVertex"]) * scal
    mesh.vert.zpos = np.array(data.variables["zVertex"]) * scal
    mesh.vert.xlon = np.array(data.variables["lonVertex"])
    mesh.vert.ylat = np.array(data.variables["latVertex"])
   #mesh.vert.area = \
   #    np.array(data.variables["areaTriangle"]) * scal ** 2
   #mesh.vert.kite = \
   #    np.array(data.variables["kiteAreasOnVertex"]) * scal ** 2
    mesh.vert.edge = \
        np.array(data.variables["edgesOnVertex"])
    mesh.vert.cell = \
        np.array(data.variables["cellsOnVertex"])


    xhat = (
        mesh.vert.xpos[mesh.edge.vert[:, 1] - 1] -
        mesh.vert.xpos[mesh.edge.vert[:, 0] - 1]
    )
    yhat = (
        mesh.vert.ypos[mesh.edge.vert[:, 1] - 1] -
        mesh.vert.ypos[mesh.edge.vert[:, 0] - 1]
    )
    zhat = (
        mesh.vert.zpos[mesh.edge.vert[:, 1] - 1] -
        mesh.vert.zpos[mesh.edge.vert[:, 0] - 1]
    )

    lhat = np.sqrt(xhat ** 2 + yhat ** 2 + zhat ** 2)
    
    mesh.edge.xprp = xhat / lhat
    mesh.edge.yprp = yhat / lhat
    mesh.edge.zprp = zhat / lhat


    xhat = (
        mesh.cell.xpos[mesh.edge.cell[:, 1] - 1] -
        mesh.cell.xpos[mesh.edge.cell[:, 0] - 1]
    )
    yhat = (
        mesh.cell.ypos[mesh.edge.cell[:, 1] - 1] -
        mesh.cell.ypos[mesh.edge.cell[:, 0] - 1]
    )
    zhat = (
        mesh.cell.zpos[mesh.edge.cell[:, 1] - 1] -
        mesh.cell.zpos[mesh.edge.cell[:, 0] - 1]
    )

    lhat = np.sqrt(xhat ** 2 + yhat ** 2 + zhat ** 2)
    
    mesh.edge.xnrm = xhat / lhat
    mesh.edge.ynrm = yhat / lhat
    mesh.edge.znrm = zhat / lhat


    mesh.cell.xmid = \
        cell_quad(mesh, mesh.cell.xpos, mesh.vert.xpos)
    mesh.cell.ymid = \
        cell_quad(mesh, mesh.cell.ypos, mesh.vert.ypos)
    mesh.cell.zmid = \
        cell_quad(mesh, mesh.cell.zpos, mesh.vert.zpos)

    mesh.cell.xmid, mesh.cell.ymid, mesh.cell.zmid, \
    mesh.cell.mlon, mesh.cell.mlat = to_sphere(
        mesh, mesh.cell.xmid, mesh.cell.ymid, mesh.cell.zmid)

    mesh.edge.xmid = \
        edge_quad(mesh, mesh.cell.xpos, mesh.vert.xpos)
    mesh.edge.ymid = \
        edge_quad(mesh, mesh.cell.ypos, mesh.vert.ypos)
    mesh.edge.zmid = \
        edge_quad(mesh, mesh.cell.zpos, mesh.vert.zpos)

    mesh.edge.xmid, mesh.edge.ymid, mesh.edge.zmid, \
    mesh.edge.mlon, mesh.edge.mlat = to_sphere(
        mesh, mesh.edge.xmid, mesh.edge.ymid, mesh.edge.zmid)

    mesh.vert.xmid = \
        dual_quad(mesh, mesh.cell.xpos, mesh.vert.xpos)
    mesh.vert.ymid = \
        dual_quad(mesh, mesh.cell.ypos, mesh.vert.ypos)
    mesh.vert.zmid = \
        dual_quad(mesh, mesh.cell.zpos, mesh.vert.zpos)

    mesh.vert.xmid, mesh.vert.ymid, mesh.vert.zmid, \
    mesh.vert.mlon, mesh.vert.mlat = to_sphere(
        mesh, mesh.vert.xmid, mesh.vert.ymid, mesh.vert.zmid)

    mesh.cell.area = cell_area (mesh)
    mesh.edge.area = edge_area (mesh)
    mesh.vert.area = dual_area (mesh)

    mesh.vert.kite = mesh_kite (mesh)
    mesh.edge.stub = mesh_stub (mesh)
    mesh.edge.wing = mesh_wing (mesh)
    
    mesh.edge.vlen, \
    mesh.edge.dlen = mesh_arcs (mesh)

    # can set this as 2 * A_e / l_e instead of the TRSK-CV
    # operators, as per Weller
    mesh.edge.clen = 2.0 * mesh.edge.area / mesh.edge.vlen
    #mesh.edge.clen = mesh.edge.dlen

    # local characteristic edge length, for AUST upwinding
    mesh.edge.slen = 0.5 * np.sqrt(2.0 * mesh.edge.area)

    return mesh


def mesh_kite(mesh):

#-- cell-dual overlapping areas

    kite = np.zeros((mesh.vert.size, 3), dtype=np.float64)
    kite[:, 0]+= tria_area(
        mesh.rsph,
        np.vstack((mesh.vert.xlon, mesh.vert.ylat)).T,
        np.vstack((
            mesh.cell.xlon[mesh.vert.cell[:, 0] - 1],
            mesh.cell.ylat[mesh.vert.cell[:, 0] - 1])).T,
        np.vstack((
            mesh.edge.xlon[mesh.vert.edge[:, 1] - 1],
            mesh.edge.ylat[mesh.vert.edge[:, 1] - 1])).T
    )
    kite[:, 0]+= tria_area(
        mesh.rsph,
        np.vstack((mesh.vert.xlon, mesh.vert.ylat)).T,
        np.vstack((
            mesh.cell.xlon[mesh.vert.cell[:, 0] - 1],
            mesh.cell.ylat[mesh.vert.cell[:, 0] - 1])).T,
        np.vstack((
            mesh.edge.xlon[mesh.vert.edge[:, 0] - 1],
            mesh.edge.ylat[mesh.vert.edge[:, 0] - 1])).T
    )

    kite[:, 1]+= tria_area(
        mesh.rsph,
        np.vstack((mesh.vert.xlon, mesh.vert.ylat)).T,
        np.vstack((
            mesh.cell.xlon[mesh.vert.cell[:, 1] - 1],
            mesh.cell.ylat[mesh.vert.cell[:, 1] - 1])).T,
        np.vstack((
            mesh.edge.xlon[mesh.vert.edge[:, 2] - 1],
            mesh.edge.ylat[mesh.vert.edge[:, 2] - 1])).T
    )
    kite[:, 1]+= tria_area(
        mesh.rsph,
        np.vstack((mesh.vert.xlon, mesh.vert.ylat)).T,
        np.vstack((
            mesh.cell.xlon[mesh.vert.cell[:, 1] - 1],
            mesh.cell.ylat[mesh.vert.cell[:, 1] - 1])).T,
        np.vstack((
            mesh.edge.xlon[mesh.vert.edge[:, 1] - 1],
            mesh.edge.ylat[mesh.vert.edge[:, 1] - 1])).T
    )

    kite[:, 2]+= tria_area(
        mesh.rsph,
        np.vstack((mesh.vert.xlon, mesh.vert.ylat)).T,
        np.vstack((
            mesh.cell.xlon[mesh.vert.cell[:, 2] - 1],
            mesh.cell.ylat[mesh.vert.cell[:, 2] - 1])).T,
        np.vstack((
            mesh.edge.xlon[mesh.vert.edge[:, 0] - 1],
            mesh.edge.ylat[mesh.vert.edge[:, 0] - 1])).T
    )
    kite[:, 2]+= tria_area(
        mesh.rsph,
        np.vstack((mesh.vert.xlon, mesh.vert.ylat)).T,
        np.vstack((
            mesh.cell.xlon[mesh.vert.cell[:, 2] - 1],
            mesh.cell.ylat[mesh.vert.cell[:, 2] - 1])).T,
        np.vstack((
            mesh.edge.xlon[mesh.vert.edge[:, 2] - 1],
            mesh.edge.ylat[mesh.vert.edge[:, 2] - 1])).T
    )

    return kite
    
    
def mesh_stub(mesh):

#-- edge-dual overlapping areas

    stub = np.zeros((mesh.edge.size, 2), dtype=np.float64)
    stub[:, 0] = tria_area(
        mesh.rsph,
        np.vstack((
            mesh.vert.xlon[mesh.edge.vert[:, 0] - 1],
            mesh.vert.ylat[mesh.edge.vert[:, 0] - 1])).T,
        np.vstack((
            mesh.cell.xlon[mesh.edge.cell[:, 1] - 1],
            mesh.cell.ylat[mesh.edge.cell[:, 1] - 1])).T,
        np.vstack((
            mesh.cell.xlon[mesh.edge.cell[:, 0] - 1],
            mesh.cell.ylat[mesh.edge.cell[:, 0] - 1])).T
    )
    stub[:, 1] = tria_area(
        mesh.rsph,
        np.vstack((
            mesh.vert.xlon[mesh.edge.vert[:, 1] - 1],
            mesh.vert.ylat[mesh.edge.vert[:, 1] - 1])).T,
        np.vstack((
            mesh.cell.xlon[mesh.edge.cell[:, 0] - 1],
            mesh.cell.ylat[mesh.edge.cell[:, 0] - 1])).T,
        np.vstack((
            mesh.cell.xlon[mesh.edge.cell[:, 1] - 1],
            mesh.cell.ylat[mesh.edge.cell[:, 1] - 1])).T
    )

    return stub
    
    
def mesh_wing(mesh):

#-- edge-cell overlapping areas

    wing = np.zeros((mesh.edge.size, 2), dtype=np.float64)
    wing[:, 0] = tria_area(
        mesh.rsph,
        np.vstack((
            mesh.vert.xlon[mesh.edge.vert[:, 1] - 1],
            mesh.vert.ylat[mesh.edge.vert[:, 1] - 1])).T,
        np.vstack((
            mesh.cell.xlon[mesh.edge.cell[:, 0] - 1],
            mesh.cell.ylat[mesh.edge.cell[:, 0] - 1])).T,
        np.vstack((
            mesh.vert.xlon[mesh.edge.vert[:, 0] - 1],
            mesh.vert.ylat[mesh.edge.vert[:, 0] - 1])).T
    )
    wing[:, 1] = tria_area(
        mesh.rsph,
        np.vstack((
            mesh.vert.xlon[mesh.edge.vert[:, 0] - 1],
            mesh.vert.ylat[mesh.edge.vert[:, 0] - 1])).T,
        np.vstack((
            mesh.cell.xlon[mesh.edge.cell[:, 1] - 1],
            mesh.cell.ylat[mesh.edge.cell[:, 1] - 1])).T,
        np.vstack((
            mesh.vert.xlon[mesh.edge.vert[:, 1] - 1],
            mesh.vert.ylat[mesh.edge.vert[:, 1] - 1])).T
    )

    return wing
    
    
def mesh_arcs(mesh):

#-- arc-lengths: vert and cells

    vlen = circ_dist(
        mesh.rsph, 
        np.vstack((
            mesh.vert.xlon[mesh.edge.vert[:, 0] - 1],
            mesh.vert.ylat[mesh.edge.vert[:, 0] - 1])).T,
        np.vstack((
            mesh.vert.xlon[mesh.edge.vert[:, 1] - 1],
            mesh.vert.ylat[mesh.edge.vert[:, 1] - 1])).T
    )
        
    dlen = circ_dist(
        mesh.rsph, 
        np.vstack((
            mesh.cell.xlon[mesh.edge.cell[:, 0] - 1],
            mesh.cell.ylat[mesh.edge.cell[:, 0] - 1])).T,
        np.vstack((
            mesh.cell.xlon[mesh.edge.cell[:, 1] - 1],
            mesh.cell.ylat[mesh.edge.cell[:, 1] - 1])).T
    )

    return vlen, dlen
    

def sort_mesh(mesh, sort=None):
    """
    SORT-MESH: sort cells, edges and duals in the mesh 
    to improve cache-locality.

    """
    # Authors: Darren Engwirda

    mesh.cell.ifwd = np.arange(0, mesh.cell.size) + 1
    mesh.cell.irev = np.arange(0, mesh.cell.size) + 1
    mesh.edge.ifwd = np.arange(0, mesh.edge.size) + 1
    mesh.edge.irev = np.arange(0, mesh.edge.size) + 1
    mesh.vert.ifwd = np.arange(0, mesh.vert.size) + 1
    mesh.vert.irev = np.arange(0, mesh.vert.size) + 1

    if (sort is None): return mesh

#-- 1. sort cells via RCM ordering of adjacency matrix

    mesh.cell.ifwd = \
        reverse_cuthill_mckee(cell_ladj(mesh)) + 1
    
    mesh.cell.irev = \
        np.zeros(mesh.cell.size, dtype=np.int32)
    mesh.cell.irev[
        mesh.cell.ifwd - 1] = np.arange(mesh.cell.size) + 1

    mask = mesh.cell.cell > 0
    mesh.cell.cell[mask] = \
        mesh.cell.irev[mesh.cell.cell[mask] - 1] + 0

    mask = mesh.edge.cell > 0
    mesh.edge.cell[mask] = \
        mesh.cell.irev[mesh.edge.cell[mask] - 1] + 0

    mask = mesh.vert.cell > 0
    mesh.vert.cell[mask] = \
        mesh.cell.irev[mesh.vert.cell[mask] - 1] + 0
    
    mesh.cell.xpos = mesh.cell.xpos[mesh.cell.ifwd - 1]
    mesh.cell.ypos = mesh.cell.ypos[mesh.cell.ifwd - 1]
    mesh.cell.zpos = mesh.cell.zpos[mesh.cell.ifwd - 1]
    mesh.cell.xmid = mesh.cell.xmid[mesh.cell.ifwd - 1]
    mesh.cell.ymid = mesh.cell.ymid[mesh.cell.ifwd - 1]
    mesh.cell.zmid = mesh.cell.zmid[mesh.cell.ifwd - 1]
    mesh.cell.xlon = mesh.cell.xlon[mesh.cell.ifwd - 1]
    mesh.cell.ylat = mesh.cell.ylat[mesh.cell.ifwd - 1]
    mesh.cell.area = mesh.cell.area[mesh.cell.ifwd - 1]
    mesh.cell.vert = mesh.cell.vert[mesh.cell.ifwd - 1]
    mesh.cell.edge = mesh.cell.edge[mesh.cell.ifwd - 1]
    mesh.cell.cell = mesh.cell.cell[mesh.cell.ifwd - 1]
    mesh.cell.topo = mesh.cell.topo[mesh.cell.ifwd - 1]

#-- 2. sort duals via pseudo-linear cell-wise ordering

    mesh.vert.ifwd = np.ravel(mesh.cell.vert)
    mesh.vert.ifwd = mesh.vert.ifwd[mesh.vert.ifwd > 0]

    __, imap = np.unique(mesh.vert.ifwd, return_index=True)

    mesh.vert.ifwd = mesh.vert.ifwd[np.sort(imap)]

    mesh.vert.irev = \
        np.zeros(mesh.vert.size, dtype=np.int32)
    mesh.vert.irev[
        mesh.vert.ifwd - 1] = np.arange(mesh.vert.size) + 1

    mask = mesh.cell.vert > 0
    mesh.cell.vert[mask] = \
        mesh.vert.irev[mesh.cell.vert[mask] - 1] + 0

    mask = mesh.edge.vert > 0
    mesh.edge.vert[mask] = \
        mesh.vert.irev[mesh.edge.vert[mask] - 1] + 0

    mesh.vert.xpos = mesh.vert.xpos[mesh.vert.ifwd - 1]
    mesh.vert.ypos = mesh.vert.ypos[mesh.vert.ifwd - 1]
    mesh.vert.zpos = mesh.vert.zpos[mesh.vert.ifwd - 1]
    mesh.vert.xmid = mesh.vert.xmid[mesh.vert.ifwd - 1]
    mesh.vert.ymid = mesh.vert.ymid[mesh.vert.ifwd - 1]
    mesh.vert.zmid = mesh.vert.zmid[mesh.vert.ifwd - 1]
    mesh.vert.xlon = mesh.vert.xlon[mesh.vert.ifwd - 1]
    mesh.vert.ylat = mesh.vert.ylat[mesh.vert.ifwd - 1]
    mesh.vert.area = mesh.vert.area[mesh.vert.ifwd - 1]
    mesh.vert.kite = mesh.vert.kite[mesh.vert.ifwd - 1]
    mesh.vert.edge = mesh.vert.edge[mesh.vert.ifwd - 1]
    mesh.vert.cell = mesh.vert.cell[mesh.vert.ifwd - 1]

#-- 3. sort edges via pseudo-linear cell-wise ordering

    mesh.edge.ifwd = np.ravel(mesh.cell.edge)
    mesh.edge.ifwd = mesh.edge.ifwd[mesh.edge.ifwd > 0]

    __, imap = np.unique(mesh.edge.ifwd, return_index=True)

    mesh.edge.ifwd = mesh.edge.ifwd[np.sort(imap)]

    mesh.edge.irev = \
        np.zeros(mesh.edge.size, dtype=np.int32)
    mesh.edge.irev[
        mesh.edge.ifwd - 1] = np.arange(mesh.edge.size) + 1

    mask = mesh.cell.edge > 0
    mesh.cell.edge[mask] = \
        mesh.edge.irev[mesh.cell.edge[mask] - 1] + 0

    mask = mesh.edge.edge > 0
    mesh.edge.edge[mask] = \
        mesh.edge.irev[mesh.edge.edge[mask] - 1] + 0

    mask = mesh.vert.edge > 0
    mesh.vert.edge[mask] = \
        mesh.edge.irev[mesh.vert.edge[mask] - 1] + 0

    mesh.edge.xpos = mesh.edge.xpos[mesh.edge.ifwd - 1]
    mesh.edge.ypos = mesh.edge.ypos[mesh.edge.ifwd - 1]
    mesh.edge.zpos = mesh.edge.zpos[mesh.edge.ifwd - 1]
    mesh.edge.xmid = mesh.edge.xmid[mesh.edge.ifwd - 1]
    mesh.edge.ymid = mesh.edge.ymid[mesh.edge.ifwd - 1]
    mesh.edge.zmid = mesh.edge.zmid[mesh.edge.ifwd - 1]
    mesh.edge.xprp = mesh.edge.xprp[mesh.edge.ifwd - 1]
    mesh.edge.yprp = mesh.edge.yprp[mesh.edge.ifwd - 1]
    mesh.edge.zprp = mesh.edge.zprp[mesh.edge.ifwd - 1]
    mesh.edge.xnrm = mesh.edge.xnrm[mesh.edge.ifwd - 1]
    mesh.edge.ynrm = mesh.edge.ynrm[mesh.edge.ifwd - 1]
    mesh.edge.znrm = mesh.edge.znrm[mesh.edge.ifwd - 1]
    mesh.edge.xlon = mesh.edge.xlon[mesh.edge.ifwd - 1]
    mesh.edge.ylat = mesh.edge.ylat[mesh.edge.ifwd - 1]
    mesh.edge.area = mesh.edge.area[mesh.edge.ifwd - 1]
    mesh.edge.vlen = mesh.edge.vlen[mesh.edge.ifwd - 1]
    mesh.edge.dlen = mesh.edge.dlen[mesh.edge.ifwd - 1]
    mesh.edge.clen = mesh.edge.clen[mesh.edge.ifwd - 1]
    mesh.edge.slen = mesh.edge.slen[mesh.edge.ifwd - 1]
    mesh.edge.stub = mesh.edge.stub[mesh.edge.ifwd - 1]
    mesh.edge.wing = mesh.edge.wing[mesh.edge.ifwd - 1]
    mesh.edge.vert = mesh.edge.vert[mesh.edge.ifwd - 1]
    mesh.edge.wmul = mesh.edge.wmul[mesh.edge.ifwd - 1]
    mesh.edge.cell = mesh.edge.cell[mesh.edge.ifwd - 1]
    mesh.edge.edge = mesh.edge.edge[mesh.edge.ifwd - 1]
    mesh.edge.topo = mesh.edge.topo[mesh.edge.ifwd - 1]

    return mesh


def load_flow(name, mesh=None, lean=False):
    """
    LOAD-FLOW: load the NAME.nc MPAS mesh file into a
    local flow data structure.

    """

    class base: pass

    data = Dataset(name, "r")

    step = int(data.dimensions["Time"].size)
    ncel = int(data.dimensions["nCells"].size)
    nedg = int(data.dimensions["nEdges"].size)
    nvrt = int(data.dimensions["nVertices"].size)
    nlev = int(data.dimensions["nVertLevels"].size)

    flow = base()

    if ("config_gravity" in data.ncattrs()):
        flow.grav = float(data.config_gravity)
    else:
        flow.grav = 9.80616

    flow.hh_cell = np.zeros((step, ncel, nlev), dtype=float)

    flow.zb_cell = np.zeros((ncel), dtype=float)
    flow.ff_cell = np.zeros((ncel), dtype=float)
    flow.ff_edge = np.zeros((nedg), dtype=float)
    flow.ff_vert = np.zeros((nvrt), dtype=float)

    flow.uu_edge = np.zeros((step, nedg, nlev), dtype=float)
    
    if ("h" in data.variables.keys()):
        flow.hh_cell = np.array(data.variables["h"])
    if ("h_s" in data.variables.keys()):
        flow.zb_cell = np.array(data.variables["h_s"])

    if ("fCell" in data.variables.keys()):
        flow.ff_cell = np.array(data.variables["fCell"])
    if ("fEdge" in data.variables.keys()):
        flow.ff_edge = np.array(data.variables["fEdge"])
    if ("fVertex" in data.variables.keys()):
        flow.ff_vert = np.array(data.variables["fVertex"])
    
    if ("u" in data.variables.keys()):
        flow.uu_edge = np.array(data.variables["u"])
    
    if ("hh_cell" in data.variables.keys()):
        flow.hh_cell = np.array(data.variables["hh_cell"])
    if ("zb_cell" in data.variables.keys()):
        flow.zb_cell = np.array(data.variables["zb_cell"])
        
    if ("ff_cell" in data.variables.keys()):
        flow.ff_cell = np.array(data.variables["ff_cell"])
    if ("ff_edge" in data.variables.keys()):
        flow.ff_edge = np.array(data.variables["ff_edge"])
    if ("ff_vert" in data.variables.keys()):
        flow.ff_vert = np.array(data.variables["ff_vert"])
    
    if ("uu_edge" in data.variables.keys()):
        flow.uu_edge = np.array(data.variables["uu_edge"])
    
    if (lean is True): return sort_flow(flow, mesh, lean)
      
    flow.vv_edge = np.zeros((step, nedg, nlev), dtype=float)

    flow.ke_cell = np.zeros((step, ncel, nlev), dtype=float)
    flow.ke_dual = np.zeros((step, nvrt, nlev), dtype=float)

    flow.rv_cell = np.zeros((step, ncel, nlev), dtype=float)
    flow.pv_cell = np.zeros((step, ncel, nlev), dtype=float)
    flow.rv_dual = np.zeros((step, nvrt, nlev), dtype=float)
    flow.pv_dual = np.zeros((step, nvrt, nlev), dtype=float)

    if ("v" in data.variables.keys()):
        flow.vv_edge = np.array(data.variables["v"])

    if ("vv_edge" in data.variables.keys()):
        flow.vv_edge = np.array(data.variables["vv_edge"])

    if ("ke_cell" in data.variables.keys()):
        flow.ke_cell = np.array(data.variables["ke_cell"])
    if ("ke_dual" in data.variables.keys()):
        flow.ke_dual = np.array(data.variables["ke_dual"])

    if ("rv_cell" in data.variables.keys()):
        flow.rv_cell = np.array(data.variables["rv_cell"])
    if ("pv_cell" in data.variables.keys()):
        flow.pv_cell = np.array(data.variables["pv_cell"])

    if ("rv_dual" in data.variables.keys()):
        flow.rv_dual = np.array(data.variables["rv_dual"])
    if ("pv_dual" in data.variables.keys()):
        flow.pv_dual = np.array(data.variables["pv_dual"])

    return sort_flow(flow, mesh, lean)
    
    
def sort_flow(flow, mesh=None, lean=False):

    if (mesh is None): return flow

    flow.hh_cell = flow.hh_cell[:, mesh.cell.ifwd - 1, :]

    flow.zb_cell = flow.zb_cell[mesh.cell.ifwd - 1]

    flow.ff_vert = flow.ff_vert[mesh.vert.ifwd - 1]
    flow.ff_edge = flow.ff_edge[mesh.edge.ifwd - 1]
    flow.ff_cell = flow.ff_cell[mesh.cell.ifwd - 1]
    
    flow.uu_edge = flow.uu_edge[:, mesh.edge.ifwd - 1, :]
    
    if (lean is True): return flow
    
    flow.vv_edge = flow.vv_edge[:, mesh.edge.ifwd - 1, :]

    flow.ke_cell = flow.ke_cell[:, mesh.cell.ifwd - 1, :]
    flow.ke_dual = flow.ke_dual[:, mesh.vert.ifwd - 1, :]

    flow.rv_cell = flow.rv_cell[:, mesh.cell.ifwd - 1, :]
    flow.rv_dual = flow.rv_dual[:, mesh.vert.ifwd - 1, :]
    flow.pv_cell = flow.pv_cell[:, mesh.cell.ifwd - 1, :]
    flow.pv_dual = flow.pv_dual[:, mesh.vert.ifwd - 1, :]

    return flow
    

def cell_ladj(mesh):

#-- form cellwise sparse adjacency graph

    xvec = np.array([], dtype=np.int32)
    ivec = np.array([], dtype=np.int32)
    jvec = np.array([], dtype=np.int32)

    for edge in range(np.max(mesh.cell.topo)):

        mask = mesh.cell.topo > edge

        cidx = np.argwhere(mask).ravel()

        aidx = mesh.cell.cell[mask, edge] - 1

        vals = np.ones(
            aidx.size, dtype=np.int32)

        ivec = np.hstack((ivec, cidx))
        jvec = np.hstack((jvec, aidx))
        xvec = np.hstack((xvec, vals))

    return csr_matrix((xvec, (ivec, jvec)))


def tria_area(rs, pa, pb, pc):

    lena = circ_dist(1., pa, pb)
    lenb = circ_dist(1., pb, pc)
    lenc = circ_dist(1., pc, pa)

    slen = 0.5 * (lena + lenb + lenc)

    tana = np.tan(0.5 * (slen - lena))
    tanb = np.tan(0.5 * (slen - lenb))
    tanc = np.tan(0.5 * (slen - lenc))

    edel = 4.0 * np.arctan(np.sqrt(
        np.tan(0.5 * slen) * tana * tanb * tanc))

    return edel * rs ** 2


def circ_dist(rs, pa, pb):

    dlon = .5 * (pa[:, 0] - pb[:, 0])
    dlat = .5 * (pa[:, 1] - pb[:, 1])

    dist = 2. * rs * np.arcsin(np.sqrt(
        np.sin(dlat) ** 2 +
        np.sin(dlon) ** 2 * np.cos(pa[:, 1]) * np.cos(pb[:, 1])
    ))

    return dist


def cell_area(mesh):
    
    pcel = np.vstack(
        (mesh.cell.xlon, mesh.cell.ylat)).T
    pvrt = np.vstack(
        (mesh.vert.xlon, mesh.vert.ylat)).T

    abar = np.zeros(mesh.cell.size, dtype=np.float64)
    
    rsph = mesh.rsph

    for epos in range(np.max(mesh.cell.topo)):

        mask = mesh.cell.topo > epos

        cidx = np.argwhere(mask).ravel()

        ifac = mesh.cell.edge[mask, epos] - 1

        ivrt = mesh.edge.vert[ifac, 0] - 1
        jvrt = mesh.edge.vert[ifac, 1] - 1

        atri = tria_area(
            rsph, pcel[cidx], pvrt[ivrt], pvrt[jvrt])

        abar[cidx] += atri
        
    return abar


def cell_quad(mesh, fcel, fvrt):
    
    pcel = np.vstack(
        (mesh.cell.xlon, mesh.cell.ylat)).T
    pvrt = np.vstack(
        (mesh.vert.xlon, mesh.vert.ylat)).T

    abar = np.zeros(mesh.cell.size, dtype=np.float64)
    fbar = np.zeros(mesh.cell.size, dtype=np.float64)

    rsph = mesh.rsph

    for epos in range(np.max(mesh.cell.topo)):

        mask = mesh.cell.topo > epos

        cidx = np.argwhere(mask).ravel()

        ifac = mesh.cell.edge[mask, epos] - 1

        ivrt = mesh.edge.vert[ifac, 0] - 1
        jvrt = mesh.edge.vert[ifac, 1] - 1

        atri = tria_area(
            rsph, pcel[cidx], pvrt[ivrt], pvrt[jvrt])

        ftri = (fcel[cidx] + fvrt[ivrt] + fvrt[jvrt])

        abar[cidx] += atri
        fbar[cidx] += atri * ftri / 3.0

    return fbar / abar


def edge_area(mesh):

    pcel = np.vstack(
        (mesh.cell.xlon, mesh.cell.ylat)).T
    pvrt = np.vstack(
        (mesh.vert.xlon, mesh.vert.ylat)).T

    abar = np.zeros(mesh.edge.size, dtype=np.float64)
    
    rsph = mesh.rsph

    for epos in range(1):

        eidx = np.arange(0, mesh.edge.size)

        ivrt = mesh.edge.vert[eidx, 0] - 1
        jvrt = mesh.edge.vert[eidx, 1] - 1

        icel = mesh.edge.cell[eidx, 0] - 1
        jcel = mesh.edge.cell[eidx, 1] - 1

        atri = tria_area(
            rsph, pvrt[ivrt], pcel[icel], pcel[jcel])

        abar[eidx] += atri

        atri = tria_area(
            rsph, pvrt[jvrt], pcel[jcel], pcel[icel])

        abar[eidx] += atri

    return abar


def edge_quad(mesh, fcel, fvrt):

    pcel = np.vstack(
        (mesh.cell.xlon, mesh.cell.ylat)).T
    pvrt = np.vstack(
        (mesh.vert.xlon, mesh.vert.ylat)).T

    abar = np.zeros(mesh.edge.size, dtype=np.float64)
    fbar = np.zeros(mesh.edge.size, dtype=np.float64)

    rsph = mesh.rsph

    for epos in range(1):

        eidx = np.arange(0, mesh.edge.size)

        ivrt = mesh.edge.vert[eidx, 0] - 1
        jvrt = mesh.edge.vert[eidx, 1] - 1

        icel = mesh.edge.cell[eidx, 0] - 1
        jcel = mesh.edge.cell[eidx, 1] - 1

        atri = tria_area(
            rsph, pvrt[ivrt], pcel[icel], pcel[jcel])

        ftri = (fvrt[ivrt] + fcel[icel] + fcel[jcel])

        abar[eidx] += atri
        fbar[eidx] += atri * ftri / 3.0

        atri = tria_area(
            rsph, pvrt[jvrt], pcel[jcel], pcel[icel])

        ftri = (fvrt[jvrt] + fcel[jcel] + fcel[icel])

        abar[eidx] += atri
        fbar[eidx] += atri * ftri / 3.0

    return fbar / abar


def dual_area(mesh):

    pcel = np.vstack(
        (mesh.cell.xlon, mesh.cell.ylat)).T
    pvrt = np.vstack(
        (mesh.vert.xlon, mesh.vert.ylat)).T

    abar = np.zeros(mesh.vert.size, dtype=np.float64)

    rsph = mesh.rsph

    for epos in range(3):

        vidx = np.arange(0, mesh.vert.size)

        ifac = mesh.vert.edge[vidx, epos] - 1

        icel = mesh.edge.cell[ifac, 0] - 1
        jcel = mesh.edge.cell[ifac, 1] - 1

        atri = tria_area(
            rsph, pvrt[vidx], pcel[icel], pcel[jcel])

        abar[vidx] += atri
        
    return abar


def dual_quad(mesh, fcel, fvrt):

    pcel = np.vstack(
        (mesh.cell.xlon, mesh.cell.ylat)).T
    pvrt = np.vstack(
        (mesh.vert.xlon, mesh.vert.ylat)).T

    abar = np.zeros(mesh.vert.size, dtype=np.float64)
    fbar = np.zeros(mesh.vert.size, dtype=np.float64)

    rsph = mesh.rsph

    for epos in range(3):

        vidx = np.arange(0, mesh.vert.size)

        ifac = mesh.vert.edge[vidx, epos] - 1

        icel = mesh.edge.cell[ifac, 0] - 1
        jcel = mesh.edge.cell[ifac, 1] - 1

        atri = tria_area(
            rsph, pvrt[vidx], pcel[icel], pcel[jcel])

        ftri = (fvrt[vidx] + fcel[icel] + fcel[jcel])

        abar[vidx] += atri
        fbar[vidx] += atri * ftri / 3.0

    return fbar / abar


def to_sphere(mesh, xpos, ypos, zpos):

    radii = mesh.rsph * np.ones((3), dtype=np.float64)
    
    xmid = 0.5 * xpos
    ymid = 0.5 * ypos
    zmid = 0.5 * zpos

    ax = xmid ** 1 / radii[0] ** 1
    ay = ymid ** 1 / radii[1] ** 1
    az = zmid ** 1 / radii[2] ** 1

    aa = ax ** 2 + ay ** 2 + az ** 2

    bx = xmid ** 2 / radii[0] ** 2
    by = ymid ** 2 / radii[1] ** 2
    bz = zmid ** 2 / radii[2] ** 2

    bb = bx * 2. + by * 2. + bz * 2.

    cx = xmid ** 1 / radii[0] ** 1
    cy = ymid ** 1 / radii[1] ** 1
    cz = zmid ** 1 / radii[2] ** 1

    cc = cx ** 2 + cy ** 2 + cz ** 2
    cc = cc - 1.0

    ts = bb * bb - 4. * aa * cc

    ok = ts >= .0

    AA = aa[ok]; BB = bb[ok]; CC = cc[ok]; TS = ts[ok]

    t1 = (-BB + np.sqrt(TS)) / AA / 2.0
    t2 = (-BB - np.sqrt(TS)) / AA / 2.0

    tt = np.maximum(t1, t2)
    
    xprj = np.zeros(xpos.shape, dtype=np.float64)
    xprj[ok] = (1. + tt) * xmid[ok]
    
    yprj = np.zeros(ypos.shape, dtype=np.float64)
    yprj[ok] = (1. + tt) * ymid[ok]    

    zprj = np.zeros(zpos.shape, dtype=np.float64)
    zprj[ok] = (1. + tt) * zmid[ok]

    xrad = xprj * radii[1]
    yrad = yprj * radii[0]
    zrad = zprj / radii[2]

    zrad = np.maximum(np.minimum(zrad, +1.), -1.)

    ylat = np.arcsin(zrad)
    xlon = np.arctan2(yrad, xrad)

    return xprj, yprj, zprj, xlon, ylat
