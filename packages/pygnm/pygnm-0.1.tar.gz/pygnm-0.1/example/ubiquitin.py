"""This is an example use of PyGNM, and is distributed with PyGNM package.

This example assumes that you have installed Matplotlib.
In this example a ubiquitin structure is used.
(PDB id 2BWF, Lowe et al., 2006 Acta Crystallogr., Sect. D 62:177)

"""

# Import plotting library
import matplotlib.pyplot as pl

# Import GNM module from pygnm package
from pygnm import GNM

# Initialize a GNM object
gnm = GNM('2BWF.pdb.gz')

# Select residues to be included in the model
# Some examples are
#	 "*" and "*:*"
#	   select all chains and residues
#
#	 "A:x,y-z,w D:k-l G:*"
#	   select residues x, y to z (inclusive),
#	                and w in chain A
#	   and residues k to l (inclusive) in chain D
#	   and all residues in chain G
#
#	 "A B"
#	   select all residues in chains A and B
#
#	 "*:5-25,50-100"
#	   select same set of residues in all chains
gnm.select_residues('A:1-70')

# Build Kirchhoff matrix
#   cutoff=10., gamma=1.0 are default values, and may be omitted
gnm.set_kirchhoff(cutoff=10., gamma=1.0)

# Calculate GNM modes
#   An optional parameter is n_modes
#   If you want to see only 20 nonzero modes, you can set n_modes=20
#   gnm.calculate_modes(n_modes=20)  
gnm.calculate_modes()

# CONVENIENCE FUNCTIONS
# Get first 20 eigenvalues, including the zero eigenvalue
gnm.get_eigenvalues( range(20) )
# Get first eigenvector with a nonzero eigenvalue
gnm.get_eigenvectors(1)
# Get first and second modes (eigenvector^2) with nonzero eigenvalues
gnm.get_modes( [1, 2] )
# Get covariance matrix (pseudo-inverse of Kirchhoff)
gnm.get_covariance()
# Get cross-correlations calclated using first 9 modes (w/ nonzero eigenvalues)
gnm.get_cross_correlations( range(1, 10))

# PLOTTING FUNCTIONS
# Note that before each plot command, pl.figure() function is called
# to prevent plotting over the previous figure.
# Plot eigenvector shape
pl.figure()
gnm.plot_eigenvector(1)

# Plot mode shape
pl.figure()
gnm.plot_mode(1)

# Plot bfactors from PDB file
pl.figure()
gnm.plot_bfactors()

# Plot GNM square-fluctuations
pl.figure()
gnm.plot_square_fluctuations()

# Plot GNM square-fluctuations for low frequence nonzero 10 modes
pl.figure()
gnm.plot_square_fluctuations(indices=range(1, 11))

# Plot GNM cross-correlations
pl.figure()
gnm.show_cross_correlations()

# Plot GNM cross-correlations for low frequence nonzero 10 modes
pl.figure()
gnm.show_cross_correlations(indices=range(1, 11))

# WRITE PDB 
# Write a PDB file with square fluctuations on beta column
# This file can be used for visualization purposes.
gnm.write_pdb( bfactors=gnm.get_square_fluctuations(indices=range(1, 11)) )

