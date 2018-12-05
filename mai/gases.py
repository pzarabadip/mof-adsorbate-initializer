from ase.build import molecule
from ase.geometry import get_distances
import numpy as np

def add_CH4_SS(site_idx,ads_pos,atoms):
	"""
	Add CH4 to the structure

	Args:
		site_idx (int): ASE index of site based on single-site model

		ads_pos (array): 1D numpy array for the best adsorbate position
		
		atoms (ASE Atoms object): Atoms object of structure
	
	Returns:
		atoms (ASE Atoms object): new ASE Atoms object with adsorbate
	
		n_new_atoms (int): number of atoms in adsorbate
	"""
	#Get CH4 parameters
	CH4 = molecule('CH4')
	CH_length = CH4.get_distance(0,1)
	CH_angle = CH4.get_angle(1,0,2)
	CH2_dihedral = CH4.get_dihedral(2,1,0,4)
	CH_length = CH4.get_distance(0,1)
	CH_angle = CH4.get_angle(1,0,2)
	CH_dihedral = CH4.get_dihedral(2,1,0,4)

	#Add CH4 to ideal adsorption position
	CH4[0].position = ads_pos

	#Make one of the H atoms colinear with adsorption site and C
	D,D_len = get_distances([ads_pos],atoms[site_idx].position,cell=atoms.cell,pbc=atoms.pbc)
	r_vec = D[0,0]
	r = (r_vec/np.linalg.norm(r_vec))*CH_length

	#Construct rest of CH4 using Z-matrix format
	CH4[1].position = ads_pos+r
	CH4.set_distance(0,2,CH_length,fix=0)
	CH4.set_angle(1,0,2,CH_angle)
	CH4.set_distance(0,3,CH_length,fix=0)
	CH4.set_angle(1,0,3,CH_angle)
	CH4.set_dihedral(2,1,0,3,-CH_dihedral)
	CH4.set_distance(0,4,CH_length,fix=0)
	CH4.set_angle(1,0,4,CH_angle)
	CH4.set_dihedral(2,1,0,4,CH2_dihedral)

	#Add CH4 molecule to the structure
	atoms.extend(CH4)
	atoms.wrap()
	
	return atoms, len(CH4)

def add_diatomic(site_idx,ads_pos,atoms,atom1,atom2=None,d_bond=2.0,angle=180.0):
	"""
	Add diatomic to the structure

	Args:
		site_idx (int): ASE index of site
		
		ads_pos (array): 1D numpy array for the best adsorbate position
		
		atoms (ASE Atoms object): Atoms object of structure
	
		angle (float): angle of site-atom1-atom2 (default of linear)'

	Returns:
		atoms (ASE Atoms object): new ASE Atoms object with adsorbate
	
		n_new_atoms (int): number of atoms in adsorbate
	"""
	#Get N2 parameters

	if atom2 is None:
		atom2 = atom1


	D,D_len = get_distances([ads_pos],atoms[site_idx].position,cell=atoms.cell,pbc=atoms.pbc)
	r_vec = D[0,0]
	r_N = (r_vec/np.linalg.norm(r_vec))*NN_length

	#Construct N2
	N2[0].position = ads_pos
	N2[1].position = ads_pos+r_N

	#Add N2 molecule to the structure
	if site_idx is None:
		raise ValueError('Site index must not be None')
	atoms.extend(N2)
	atoms.wrap()
	atoms.set_angle(site_idx,-2,-1,angle=angle,indices=-1)

	return atoms, len(N2)

def add_triatomic():

	return