        from hedge.discretization import ones_on_boundary
        bdry1 = ones_on_boundary(discr, None)
        silo = SiloFile("bdry.silo")
        vis.add_to_silo(silo,
                scalars=[("bdry", bdry1)],
                write_coarse_mesh=True,
                )
        return

        from hedge.visualization import SiloVisualizer
        from hedge.silo import SiloFile, DB_CLOBBER
        vis = SiloVisualizer(self.discr)
        silo = SiloFile("flux.silo", mode=DB_CLOBBER)
        vis.add_to_silo(silo,
                vectors=[
                    ("int_h", cross(self.n_jump, h)),
                    ("bdry_h", cross(self.n_jump, h_pair)),
                    ],
                write_coarse_mesh=True,
                )
        silo.close()
        raw_input("Enter:")

