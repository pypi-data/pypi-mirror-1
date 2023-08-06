
    def rhs_weak(t, u):
        from pytools import argmax

        central_nx = CentralWeak(0)
        central_ny = CentralWeak(1)

        bc = discr.interpolate_boundary_function("inflow",
                lambda x: u_analytic(t, x))

        rhsint =   -a[0]*discr.apply_stiffness_matrix_t(0, u)
                #+ a[1]*discr.differentiate(1, u)
        rhsflux =  a[0]*discr.lift_interior_flux(central_nx, u)
                #-  a[1]*discr.lift_interior_flux(central_ny, u)
        rhsbdry = \
                   a[0]*discr.lift_boundary_flux("inflow", 
                           central_nx, u, bc)
                #-  a[1]*discr.lift_boundary_flux(central_ny, u, bc,
                        #"inflow")

        if False:
            maxidx = argmax(rhsflux)
            print "MAXES", max(rhsflux), maxidx, discr.find_face(maxidx)
            raw_input()

        mflux = discr.apply_inverse_mass_matrix(rhsflux+rhsbdry)
        #if False:
        if rhscnt[0] % rhsstep == 0 or rhscnt[0] < 10:
            discr.visualize_vtk("rhs-%04d.vtk" % rhscnt[0],
                    [
                        ("u", u),
                        ("s_u", sym_map(u)),
                        ("int", rhsint), 
                        ("iflux", rhsflux),
                        ("bdry", rhsbdry),
                        ("rhs", rhsint+rhsflux+rhsbdry),
                        ("flux", rhsflux+rhsbdry),
                        ("mflux", mflux),
                        ])
        rhscnt[0] += 1

        return rhsint+mflux

