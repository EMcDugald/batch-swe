
import time
import numpy as np

""" SWE time integration via various Runge-Kutta methods
"""
#-- Darren Engwirda, Jeremy Lilly

from _dx import computeCd
from _dx import tcpu
from rhs import rhs_all_u, rhs_all_h, \
                rhs_slw_u, rhs_fst_u, rhs_fst_h

def step_eqns(mesh, trsk, flow, cnfg, 
              hh_cell, uu_edge,     # state
              ht_cell, ut_edge):    # time-derivatives

#-- operator splitting for drag terms

    BIAS = 5.0 / 9.0  # theta method centre

    if (cnfg.loglaw_z0 > 0.):
    #-- 1st part of bot. drag strang splits
        ttic = time.time()

        cd_edge = computeCd(
            mesh, trsk, cnfg, hh_cell, uu_edge)

    #-- theta scheme: explicit tend.
        us_edge = uu_edge - 0.5 * cnfg.time_step * \
            (1. - BIAS) * cd_edge * uu_edge

    #-- theta scheme: implicit solve
        us_edge/= (1. + 
            0.5 * BIAS * cnfg.time_step * cd_edge)

        ttoc = time.time()
        tcpu.computeCd = \
            tcpu.computeCd + (ttoc - ttic)

    else:
    #-- zero bot. drag: no operator split needed
        us_edge = uu_edge[:]

    #-- step the rest of the shallow-water eqn's

    if ("RK22" in cnfg.integrate):

        hs_cell, us_edge, \
        ht_cell, ut_edge = step_RK22(
            mesh, trsk, flow, cnfg, 
            hh_cell, us_edge, ht_cell, ut_edge)

    if ("RK32" in cnfg.integrate):

        hs_cell, us_edge, \
        ht_cell, ut_edge = step_RK32(
            mesh, trsk, flow, cnfg, 
            hh_cell, us_edge, ht_cell, ut_edge)

    if ("SP33" in cnfg.integrate):

        hs_cell, us_edge, \
        ht_cell, ut_edge = step_SP33(
            mesh, trsk, flow, cnfg, 
            hh_cell, us_edge, ht_cell, ut_edge)

    if ("RK44" in cnfg.integrate):

        hs_cell, us_edge, \
        ht_cell, ut_edge = step_RK44(
            mesh, trsk, flow, cnfg, 
            hh_cell, us_edge, ht_cell, ut_edge)

    if ("SF32" in cnfg.integrate):

        hs_cell, us_edge, \
        ht_cell, ut_edge = step_SF32(
            mesh, trsk, flow, cnfg, 
            hh_cell, us_edge, ht_cell, ut_edge)


    if (cnfg.loglaw_z0 > 0.):
    #-- 2nd part of bot. drag strang splits
        ttic = time.time()

        cd_edge = computeCd(
            mesh, trsk, cnfg, hs_cell, us_edge)

    #-- theta scheme: explicit tend.
        us_edge = us_edge - 0.5 * cnfg.time_step * \
            (1. - BIAS) * cd_edge * us_edge

    #-- theta scheme: implicit solve
        us_edge/= (1. + 
            0.5 * BIAS * cnfg.time_step * cd_edge)

        ttoc = time.time()
        tcpu.computeCd = \
            tcpu.computeCd + (ttoc - ttic)

    return hs_cell, us_edge, ht_cell, ut_edge


def step_RK22(mesh, trsk, flow, cnfg, 
              hh_cell, uu_edge,     # state
              ht_cell, ut_edge):    # time-derivatives

#-- A 2-stage RK + FB scheme, a'la ROMS:
#-- A.F. Shchepetkin, J.C. McWilliams (2005): The regional oceanic 
#-- modeling system (ROMS): a split-explicit, free-surface, 
#-- topography-following-coordinate oceanic model
#-- doi.org/10.1016/j.ocemod.2004.08.002

#-- but with thickness updated via an SSP-RK2 approach

#-- 1st RK + FB stage

    ttic = time.time()

    if cnfg.fb_weight:
        BETA = cnfg.fb_weight[0]
    else:
        BETA = 0.333333333333333

    BETA *= ("FB" in cnfg.integrate)

    rh_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, hh_cell, uu_edge)

    h1_cell = (
        hh_cell - 1.0 / 1.0 * cnfg.time_step * rh_cell
    )

    ht_cell = (h1_cell - hh_cell) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    hb_cell = h1_cell * (0.0 + 1.0 * BETA) + \
              hh_cell * (1.0 - 1.0 * BETA)

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            hb_cell, uu_edge, ht_cell, ut_edge)

    u1_edge = (
        uu_edge - 1.0 / 1.0 * cnfg.time_step * ru_edge
    )

    ut_edge = (u1_edge - uu_edge) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 2nd RK + FB stage

    ttic = time.time()

    if cnfg.fb_weight:
        BETA = cnfg.fb_weight[1]
    else:
        BETA = 0.666666666666667

    BETA *= ("FB" in cnfg.integrate)

    hm_cell = 0.5 * hh_cell + 0.5 * h1_cell
    um_edge = 0.5 * uu_edge + 0.5 * u1_edge

    rh_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, h1_cell, u1_edge)

    h2_cell = (
        hm_cell - 1.0 / 2.0 * cnfg.time_step * rh_cell
    )

    ht_cell = (h2_cell - hh_cell) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    hb_cell = h2_cell * (0.0 + 0.5 * BETA) + \
              h1_cell * (0.5 - 0.5 * BETA) + \
              hh_cell * (0.5)

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            hb_cell, um_edge, ht_cell, ut_edge)

    u2_edge = (
        uu_edge - 1.0 / 1.0 * cnfg.time_step * ru_edge
    )

    ut_edge = (u2_edge - uu_edge) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

    return h2_cell, u2_edge, ht_cell, ut_edge


def step_RK32(mesh, trsk, flow, cnfg, 
              hh_cell, uu_edge,     # state
              ht_cell, ut_edge):    # time-derivatives

#-- A 3-stage RK scheme, a'la MPAS-A:
#-- L.J. Wicker, W.C. Skamarock (2002): Time-Splitting Methods for 
#-- Elastic Models Using Forward Time Schemes
#-- doi.org/10.1175/1520-0493(2002)130<2088:TSMFEM>2.0.CO;2

#-- but with FB weighting applied within each RK stage

#-- 1st RK + FB stage

    ttic = time.time()

    if cnfg.fb_weight:
        BETA = cnfg.fb_weight[0]
    else:
        BETA = 0.311875000000000

    BETA *= ("FB" in cnfg.integrate)

    rh_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, hh_cell, uu_edge)

    h1_cell = (
        hh_cell - 1.0 / 3.0 * cnfg.time_step * rh_cell
    )

    ht_cell = (h1_cell - hh_cell) / cnfg.time_step * 3
    
    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    hb_cell = h1_cell * (0.0 + 1.0 * BETA) + \
              hh_cell * (1.0 - 1.0 * BETA)

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            hb_cell, uu_edge, ht_cell, ut_edge)

    u1_edge = (
        uu_edge - 1.0 / 3.0 * cnfg.time_step * ru_edge
    )

    ut_edge = (u1_edge - uu_edge) / cnfg.time_step * 3

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 2nd RK + FB stage

    ttic = time.time()

    if cnfg.fb_weight:
        BETA = cnfg.fb_weight[1]
    else:
        BETA = 0.425000000000000

    BETA *= ("FB" in cnfg.integrate)

    rh_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, h1_cell, u1_edge)

    h2_cell = (
        hh_cell - 1.0 / 2.0 * cnfg.time_step * rh_cell
    )

    ht_cell = (h2_cell - hh_cell) / cnfg.time_step * 2

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    hb_cell = h2_cell * (0.0 + 1.0 * BETA) + \
              hh_cell * (1.0 - 1.0 * BETA)

    # when FB is not in use, the data for h used to advance 
    # u in the second stage needs to be manually set to 
    # the first stage data for h
    isFB = +1.0 * ("FB" in cnfg.integrate)

    hb_cell = hb_cell * (0.0 + 1.0 * isFB) + \
              h1_cell * (1.0 - 1.0 * isFB)

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            hb_cell, u1_edge, ht_cell, ut_edge)

    u2_edge = (
        uu_edge - 1.0 / 2.0 * cnfg.time_step * ru_edge
    )

    ut_edge = (u2_edge - uu_edge) / cnfg.time_step * 2

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 3rd RK + FB stage

    ttic = time.time()

    if cnfg.fb_weight:
        BETA = cnfg.fb_weight[2]
    else:
        BETA = 0.362500000000000

    BETA *= ("FB" in cnfg.integrate)

    rh_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, h2_cell, u2_edge)

    h3_cell = (
        hh_cell - 1.0 / 1.0 * cnfg.time_step * rh_cell
    )

    ht_cell = (h3_cell - hh_cell) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    hb_cell = h3_cell * (0.0 + 1.0 * BETA) + \
              h2_cell * (1.0 - 2.0 * BETA) + \
              hh_cell * (0.0 + 1.0 * BETA)

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            hb_cell, u2_edge, ht_cell, ut_edge)

    u3_edge = (
        uu_edge - 1.0 / 1.0 * cnfg.time_step * ru_edge
    )

    ut_edge = (u3_edge - uu_edge) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

    return h3_cell, u3_edge, ht_cell, ut_edge


def step_SF32(mesh, trsk, flow, cnfg, 
              hh_cell, uu_edge,     # state
              ht_cell, ut_edge):    # time-derivatives

#-- a "slow-fast" split integration scheme, based on a strang-like
#-- operator splitting...

    dt_step = cnfg.time_step

    hs_cell = hh_cell[:]
    us_edge = uu_edge[:]

#-- leading 1/4 "fast" step

    cnfg.time_step = \
        1./4. * dt_step / cnfg.sub_steps

    for subs in range(+0, cnfg.sub_steps):
        hs_cell, us_edge, \
        ht_cell, ut_edge = fast_RK32(
            mesh, trsk, flow, cnfg, 
            hs_cell, us_edge, 0., ht_cell, ut_edge)

#-- leading 1/2 "slow" step

    cnfg.time_step = 1./2. * dt_step

    hs_cell, us_edge, \
    ht_cell, ut_edge = slow_RK32(
        mesh, trsk, flow, cnfg, 
        hs_cell, us_edge, ht_cell, ut_edge)

#-- central 1/2 "fast" step

    cnfg.time_step = \
        1./4. * dt_step / cnfg.sub_steps

    for subs in range(+0, cnfg.sub_steps):
        hs_cell, us_edge, \
        ht_cell, ut_edge = fast_RK32(
            mesh, trsk, flow, cnfg, 
            hs_cell, us_edge, 0., ht_cell, ut_edge)

        hs_cell, us_edge, \
        ht_cell, ut_edge = fast_RK32(
            mesh, trsk, flow, cnfg, 
            hs_cell, us_edge, 0., ht_cell, ut_edge)

#-- tailing 1/2 "slow" step

    cnfg.time_step = 1./2. * dt_step

    hs_cell, us_edge, \
    ht_cell, ut_edge = slow_RK32(
        mesh, trsk, flow, cnfg, 
        hs_cell, us_edge, ht_cell, ut_edge)

#-- tailing 1/2 "fast" step
    cnfg.time_step = \
        1./4. * dt_step / cnfg.sub_steps

    for subs in range(+0, cnfg.sub_steps):
        hs_cell, us_edge, \
        ht_cell, ut_edge = fast_RK32(
            mesh, trsk, flow, cnfg, 
            hs_cell, us_edge, 0., ht_cell, ut_edge)
    
    cnfg.time_step = 1.0 * dt_step  # reset for next

    return hs_cell, us_edge, ht_cell, ut_edge


def slow_RK32(mesh, trsk, flow, cnfg, 
              hh_cell, uu_edge,     # state
              ht_cell, ut_edge):    # time-derivatives

#-- only the "slow" momentum tendencies

#-- A 3-stage RK scheme, a'la MPAS-A:
#-- L.J. Wicker, W.C. Skamarock (2002): Time-Splitting Methods for 
#-- Elastic Models Using Forward Time Schemes
#-- doi.org/10.1175/1520-0493(2002)130<2088:TSMFEM>2.0.CO;2

#-- 1st RK + FB stage

    ttic = time.time()

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_slw_u(
        mesh, trsk, flow, cnfg, 
            hh_cell, uu_edge, ht_cell, ut_edge)

    u1_edge = (
        uu_edge - 1.0 / 3.0 * cnfg.time_step * ru_edge
    )

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 2nd RK + FB stage

    ttic = time.time()

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_slw_u(
        mesh, trsk, flow, cnfg, 
            hh_cell, u1_edge, ht_cell, ut_edge)

    u2_edge = (
        uu_edge - 1.0 / 2.0 * cnfg.time_step * ru_edge
    )

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 3rd RK + FB stage

    ttic = time.time()

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_slw_u(
        mesh, trsk, flow, cnfg, 
            hh_cell, u2_edge, ht_cell, ut_edge)

    u3_edge = (
        uu_edge - 1.0 / 1.0 * cnfg.time_step * ru_edge
    )

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

    return hh_cell, u3_edge, ht_cell, ut_edge


def fast_RK32(mesh, trsk, flow, cnfg,
              hh_cell, uu_edge,     # state
              su_edge,              # slow rhs
              ht_cell, ut_edge):    # time-derivatives

#-- only the "fast" surface wave tendencies

#-- A 3-stage RK scheme, a'la MPAS-A:
#-- L.J. Wicker, W.C. Skamarock (2002): Time-Splitting Methods for 
#-- Elastic Models Using Forward Time Schemes
#-- doi.org/10.1175/1520-0493(2002)130<2088:TSMFEM>2.0.CO;2

#-- but with FB weighting applied within each RK stage

#-- 1st RK + FB stage

    ttic = time.time()

    if cnfg.fb_weight:
        BETA = cnfg.fb_weight[0]
    else:
        BETA = 0.311875000000000

    BETA *= ("FB" in cnfg.integrate)

    rh_cell = rhs_fst_h(
        mesh, trsk, flow, cnfg, hh_cell, uu_edge)

    h1_cell = (
        hh_cell - 1.0 / 3.0 * cnfg.time_step * rh_cell
    )

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    hb_cell = h1_cell * (0.0 + 1.0 * BETA) + \
              hh_cell * (1.0 - 1.0 * BETA)

    ru_edge = rhs_fst_u(
        mesh, trsk, flow, cnfg, 
            hb_cell, uu_edge, ht_cell, ut_edge)

    if isinstance(su_edge, np.ndarray):  # skip if 0.0
        ru_edge+= su_edge

    u1_edge = (
        uu_edge - 1.0 / 3.0 * cnfg.time_step * ru_edge
    )

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 2nd RK + FB stage

    ttic = time.time()

    if cnfg.fb_weight:
        BETA = cnfg.fb_weight[1]
    else:
        BETA = 0.425000000000000

    BETA *= ("FB" in cnfg.integrate)

    rh_cell = rhs_fst_h(
        mesh, trsk, flow, cnfg, h1_cell, u1_edge)

    h2_cell = (
        hh_cell - 1.0 / 2.0 * cnfg.time_step * rh_cell
    )

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    hb_cell = h2_cell * (0.0 + 1.0 * BETA) + \
              hh_cell * (1.0 - 1.0 * BETA)

    # when FB is not in use, the data for h used to advance 
    # u in the second stage needs to be manually set to 
    # the first stage data for h
    isFB = +1.0 * ("FB" in cnfg.integrate)

    hb_cell = hb_cell * (0.0 + 1.0 * isFB) + \
              h1_cell * (1.0 - 1.0 * isFB)

    ru_edge = rhs_fst_u(
        mesh, trsk, flow, cnfg, 
            hb_cell, u1_edge, ht_cell, ut_edge)

    if isinstance(su_edge, np.ndarray):  # skip if 0.0
        ru_edge+= su_edge

    u2_edge = (
        uu_edge - 1.0 / 2.0 * cnfg.time_step * ru_edge
    )

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 3rd RK + FB stage

    ttic = time.time()

    if cnfg.fb_weight:
        BETA = cnfg.fb_weight[2]
    else:
        BETA = 0.362500000000000

    BETA *= ("FB" in cnfg.integrate)

    rh_cell = rhs_fst_h(
        mesh, trsk, flow, cnfg, h2_cell, u2_edge)

    h3_cell = (
        hh_cell - 1.0 / 1.0 * cnfg.time_step * rh_cell
    )

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    hb_cell = h3_cell * (0.0 + 1.0 * BETA) + \
              h2_cell * (1.0 - 2.0 * BETA) + \
              hh_cell * (0.0 + 1.0 * BETA)

    ru_edge = rhs_fst_u(
        mesh, trsk, flow, cnfg, 
            hb_cell, u2_edge, ht_cell, ut_edge)

    if isinstance(su_edge, np.ndarray):  # skip if 0.0
        ru_edge+= su_edge

    u3_edge = (
        uu_edge - 1.0 / 1.0 * cnfg.time_step * ru_edge
    )

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

    return h3_cell, u3_edge, ht_cell, ut_edge


def step_SP33(mesh, trsk, flow, cnfg, 
              hh_cell, uu_edge,     # state
              ht_cell, ut_edge):    # time-derivatives

#-- standard SSP-RK(3,3) method:
#-- S. Gottlieb (2005): On high order strong stability preserving 
#-- runge-kutta and multi step time discretizations
#-- doi.org/10.1007/BF02728985

#-- 1st RK stage

    ttic = time.time()

    rh_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, hh_cell, uu_edge)

    h1_cell = (
        hh_cell - 1.0 / 1.0 * cnfg.time_step * rh_cell
    )

    ht_cell = (h1_cell - hh_cell) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            hh_cell, uu_edge, ht_cell, ut_edge)

    u1_edge = (
        uu_edge - 1.0 / 1.0 * cnfg.time_step * ru_edge
    )

    ut_edge = (u1_edge - uu_edge) / cnfg.time_step * 1
    
    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 2nd RK stage

    ttic = time.time()

    rh_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, h1_cell, u1_edge)

    h2_cell = (
        3.0 / 4.0 * hh_cell + 
        1.0 / 4.0 * h1_cell - 
            1.0 / 4.0 * cnfg.time_step * rh_cell
    )

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            h1_cell, u1_edge, ht_cell, ut_edge)

    u2_edge = (
        3.0 / 4.0 * uu_edge +
        1.0 / 4.0 * u1_edge - 
            1.0 / 4.0 * cnfg.time_step * ru_edge
    )

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 3rd RK stage

    ttic = time.time()

    rh_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, h2_cell, u2_edge)

    h3_cell = (
        1.0 / 3.0 * hh_cell +
        2.0 / 3.0 * h2_cell - 
            2.0 / 3.0 * cnfg.time_step * rh_cell
    )

    ht_cell = (h3_cell - hh_cell) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    ru_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            h2_cell, u2_edge, ht_cell, ut_edge)

    u3_edge = (
        1.0 / 3.0 * uu_edge +
        2.0 / 3.0 * u2_edge - 
            2.0 / 3.0 * cnfg.time_step * ru_edge
    )

    ut_edge = (u3_edge - uu_edge) / cnfg.time_step * 1
    
    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

    return h3_cell, u3_edge, ht_cell, ut_edge


def step_RK44(mesh, trsk, flow, cnfg,
              hh_cell, uu_edge,     # state
              ht_cell, ut_edge):    # time-derivatives

#-- classical four stage, fourth order Runge-Kutta method:
#-- R. LeVeque (2007): Finite difference methods for ordinary
#-- and partial differential equations, ch. 5
#-- doi.org/10.1137/1.9780898717839.ch5

#-- 1st RK stage 

    ttic = time.time()

    rh1_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, hh_cell, uu_edge)

    h1_cell = ( 
        hh_cell - 1.0 / 2.0 * cnfg.time_step * rh1_cell
    )

    ht_cell = (h1_cell - hh_cell) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    ru1_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            hh_cell, uu_edge, ht_cell, ut_edge)
    
    u1_edge = ( 
        uu_edge - 1.0 / 2.0 * cnfg.time_step * ru1_edge
    )

    ut_edge = (u1_edge - uu_edge) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 2nd RK stage

    ttic = time.time()

    rh2_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, h1_cell, u1_edge)

    h2_cell = (
        hh_cell - 1.0 / 2.0 * cnfg.time_step * rh2_cell
    )

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    ru2_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            h1_cell, u1_edge, ht_cell, ut_edge)
    
    u2_edge = ( 
        uu_edge - 1.0 / 2.0 * cnfg.time_step * ru2_edge
    )

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 3rd RK stage

    ttic = time.time()

    rh3_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, h2_cell, u2_edge)

    h3_cell = (
        hh_cell - 1.0 / 1.0 * cnfg.time_step * rh3_cell
    )

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    ru3_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            h2_cell, u2_edge, ht_cell, ut_edge)
    
    u3_edge = ( 
        uu_edge - 1.0 / 1.0 * cnfg.time_step * ru3_edge
    )

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

#-- 4th RK stage

    ttic = time.time()

    rh4_cell = rhs_all_h(
        mesh, trsk, flow, cnfg, h3_cell, u3_edge)

    h4_cell = (
        hh_cell - 1.0 / 6.0 * cnfg.time_step * (
            rh1_cell + 
            2 * rh2_cell + 
            2 * rh3_cell +
            rh4_cell
        )
    )

    ht_cell = (h4_cell - hh_cell) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.thickness = tcpu.thickness + (ttoc - ttic)

    ttic = time.time()

    ru4_edge, \
    ke_cell, ke_dual, ke_bias, \
    rv_cell, pv_cell, \
    rv_dual, pv_dual, pv_bias = rhs_all_u(
        mesh, trsk, flow, cnfg, 
            h3_cell, u3_edge, ht_cell, ut_edge)
    
    u4_edge = ( 
        uu_edge - 1.0 / 6.0 * cnfg.time_step * (
            ru1_edge +
            2 * ru2_edge +
            2 * ru3_edge +
            ru4_edge
        )
    )

    ut_edge = (u4_edge - uu_edge) / cnfg.time_step * 1

    ttoc = time.time()
    tcpu.momentum_ = tcpu.momentum_ + (ttoc - ttic)

    return h4_cell, u4_edge, ht_cell, ut_edge


