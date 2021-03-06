Triatomics
===========

In this example, we'll work through how to add three-atom adsorbates to open metal sites in MOFs. The CIF for the MOF we'll use for this example can be found :download:`here <../examples/example_MOFs/Fe-MIL-88B.cif>`. This MOF is known as MIL-8BB and has trimetallic nodes with each metal cation in a square pyramidal geometry.

--------------------
Contiguous Adsorbate
--------------------
For this example, we will consider the initialization of a "contiguous" triatomic adsorbate. What I mean by this is that if we treat the adsorbate as an arbitrary molecule X1-X2-X3, then the adsorption process is described by M-X1-X2-X3. In this example, we'll consider the adsorption of N2O to an Fe site, in both an η1-N and η1-O binding mode. The code to handle this is shown below. 

.. literalinclude:: ../examples/add_N2O.py

Like with the previous examples, we need to initialize an :class:`~mai.adsorbate_constructor.adsorbate_constructor` object and then provide it the MOF of interest. In the case of triatomics, we have a few new keywords to introduce. In addition to the arguments described in the previous examples, we can now provide MAI additional geometric parameters if desired. Namely, the new features are now that we can include the X2-X3 bond length and the X1-X2-X3 bond angle. The arguments used here are described below:

1. The ``ads``, ``d_MX1X2``, ``d_X1X2``, and ``ang_MX1X2`` are the same as before.
2. Now, we have the option to add the ``d_X2X3`` keyword argument, which specifies the X2-X3 distance. It defaults to ``d_X2X3=d_X1X2`` if not specified.
3. We can also add the ``ang_triads`` keyword argument, which specifies the X1-X2-X3 bond angle. It defaults to ``ang_triads=180`` if not specified.

That takes care of initializing the :class:`~mai.adsorbate_constructor.adsorbate_constructor` object. With this, we provide the object with the path to the MOF, and it will initialize the adsorbate. Now let's see what happens as a result of running this code! The initialized structures are shown below:

|Fe-MIL-8BB-N2O|

Exactly what we'd expect once more! You can see that in the first example, N2O is bound in an η1-N mode, whereas the second is bound in an η1-O mode, as specified. Feel free to play around with the bond distance and bond angle arguments to get a feel for how MAI works.

.. |Fe-MIL-8BB-N2O| image:: _static/n2o.png
   :align: middle
   :scale: 50 %

---------------------
Noncontiguous Adsorbate
---------------------
The last bit of trickery comes into play when dealing with what I'll call "noncontiguous" adsorbates. These are adsorbates like water, where it is triatomic, but it is not bound in a sequential fashion. As with water, you will have a central atom of the adsorbate bound to the metal (instead of an M-O-H-H adsorption mode). To tell MAI about this desired adsorption mode, :class:`~mai.adsorbate_constructor.adsorbate_constructor` has a keyword argument named ``connect``, which is the atom number in ``ads`` that should be bound to the adsorption site. For the case of ``ads='HOH'``, we should set ``connect=2`` to have the second atom (i.e. the O atom) bound to the adsorption site. Note that for this reason we cannot use ``ads='H2O'`` here.

An example code is shown below. The main thing to keep in mind is that now the connecting atom of the adsorbate is X2 instead of X1. If not specified, ``ang_triads`` will default to ``ang_triads=ang_MX1X2`` if ``connect=2``, but here we set it to 104.5°, as is standard for H2O.

.. literalinclude:: ../examples/add_H2O.py

This results in the following initialized structure:

|Fe-MIL-8BB-H2O|

.. |Fe-MIL-8BB-H2O| image:: _static/h2o.png
   :align: middle
   :scale: 60 %

That concludes our tutorial for triatomic adsorbates.