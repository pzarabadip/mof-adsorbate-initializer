import numpy as np
import os
from ase.io import read
from mai.ads_sites import ads_pos_optimizer
from mai.tools import prep_paths, get_refcode
from mai.oms_handler import get_zeo_data, get_omd_data
from mai.NN_algos import get_NNs_pm
from mai.grid_handler import get_best_grid_pos
"""
This module provides classes to add adsorbates to a MOF
"""
class adsorbate_constructor():
	"""
	This class constructs an ASE atoms object with an adsorbate
	"""
	def __init__(self,ads_species,bond_dist,site_idx=None,site_species=None,
		d_bond=1.25,angle=None,eta=1,d_bond2=None,angle2=None,connect=1,
		r_cut=2.5,sum_tol=0.5,rmse_tol=0.25,overlap_tol=0.75):
		"""
		Initialized variables

		Args:
			ads_species (string): string of atomic element for adsorbate
			(e.g. 'O')

			bond_dist (float): distance between adsorbate and surface atom. If
			used with get_adsorbate_grid, it represents the maximum distance

			site_idx (int): ASE index for the adsorption site
			
			site_species (string): if site_idx is not specified, can specify
			the site_species as a string of the atomic element for the adsorption
			site (autoamtically picks the ASE index for the last atom of type
			site_species in the Atoms object)

			d_bond (float): X1-X2 bond length (defaults to 1.25)

			angle (float): site-X1-X2 angle (for diatomics, defaults to 180 degrees
			except for side-on in which it defaults to 90 or end-on O2 in which
			it defaults to 120; for triatomics, defaults to 180 except for H2O
			in which it defaults to 104.5)

			eta (int): denticity of end-on (1) or side-on (2) (defaults to 1)

			r_cut (float): cutoff distance for calculating nearby atoms when
			ranking adsorption sites
			
			sum_tol (float): threshold to determine planarity. when the sum
			of the Euclidean distance vectors of coordinating atoms is less
			than sum_tol, planarity is assumed
			
			rmse_tol (float): second threshold to determine planarity. when the 
			root mean square error of the best-fit plane is less than rmse_tol,
			planarity is assumed
			
			overlap_tol (float): distance below which atoms are assumed to be
			overlapping
		"""
		self.ads_species = ads_species
		self.bond_dist = bond_dist
		self.r_cut = r_cut
		self.sum_tol = sum_tol
		self.rmse_tol = rmse_tol
		self.overlap_tol = overlap_tol
		self.site_species = site_species
		self.site_idx = site_idx

		#initialize certain variables as None
		self.d_bond = d_bond
		self.d_bond2 = d_bond2
		self.angle = angle
		self.angle2 = angle2
		self.eta = eta
		self.connect = connect
		
	def get_adsorbate_grid(self,atoms_filepath,grid_path=None,
		grid_format='ASCII',write_file=True,new_mofs_path=None,error_path=None):
		"""
		This function adds a molecular adsorbate based on an ASCII-formatted
		energy grid (such as via RASPA)

		Args:
			atoms_filepath (string): filepath to the CIF file
			
			grid_path (string): path to the directory containing the PEG
			(defaults to /energy_grids within the directory containing
			the starting CIF file)

			grid_format (string): accepts either 'ASCII' or 'cube' and
			is the file format for the PEG (defaults to ASCII)

			write_file (bool): if True, the new ASE atoms object should be
			written to a CIF file (defaults to True)
			
			new_mofs_path (string): path to store the new CIF files if
			write_file is True (defaults to /new_mofs within the directory
			containing the starting CIF file)
			
			error_path (string): path to store any adsorbates flagged as
			problematic (defaults to /errors within the directory
			containing the starting CIF file)

		Returns:
			new_atoms (Atoms object): ASE Atoms object of MOF with adsorbate
			
			new_name (string): name of MOF with adsorbate
		"""
		#Check for file and prepare paths
		
		self.ads_species += '_grid'
		if not os.path.isfile(atoms_filepath):
			print('WARNING: No MOF found for '+atoms_filepath)
			return None, None

		grid_format = grid_format.lower()
		if grid_format == 'ascii':
			grid_ext = '.grid'
		elif grid_format == 'cube':
			grid_ext = '.cube'
		else:
			raise ValueError('Unsupported grid_format '+grid_format)

		if self.site_species is None and self.site_idx is None:
			raise ValueError('site_species or site_idx must be specified')

		if grid_path is None:
			grid_path = os.path.join(os.path.dirname(atoms_filepath),'energy_grids')
		if new_mofs_path is None:
			new_mofs_path = os.path.join(os.getcwd(),'new_mofs')
		if error_path is None:
			error_path = os.path.join(os.getcwd(),'errors')

		site_species = self.site_species
		max_dist = self.bond_dist

		if write_file:
			prep_paths(new_mofs_path,error_path)

		atoms_filename = os.path.basename(atoms_filepath)
		name = get_refcode(atoms_filename)
		atoms = read(atoms_filepath)
		grid_filepath = os.path.join(grid_path,name+grid_ext)

		if self.site_idx is None:
			self.site_idx = [atom.index for atom in atoms if atom.symbol == site_species][-1]
		site_idx = self.site_idx
		
		site_pos = atoms[site_idx].position
		ads_pos = get_best_grid_pos(atoms,max_dist,site_idx,grid_filepath)
		if ads_pos is 'nogrid':
			print('WARNING: no grid for '+name)
			return None, None
		elif ads_pos is 'invalid':
			print('WARNING: all NaNs within cutoff for '+name)
			return None, None
		ads_optimizer = ads_pos_optimizer(self,atoms_filepath,
					new_mofs_path=new_mofs_path,error_path=error_path)
		new_atoms, new_name = ads_optimizer.get_new_atoms_grid(site_pos,ads_pos)
		return new_atoms, new_name

	def get_adsorbate_pm(self,atoms_filepath,NN_method='crystal',write_file=True,
		new_mofs_path=None,error_path=None):
		"""
		Use Pymatgen's nearest neighbors algorithms to add an adsorbate

		Args:

			atoms_filepath (string): filepath to the CIF file
			
			NN_method (string): string representing the desired Pymatgen
			nearest neighbor algorithm. options include 'crystal',vire','okeefe',
			and others. See NN_algos.py (defaults to 'crystal')

			write_file (bool): if True, the new ASE atoms object should be
			written to a CIF file (defaults to True)
			
			new_mofs_path (string): path to store the new CIF files if
			write_file is True (defaults to /new_mofs within the directory
			containing the starting CIF file)
			
			error_path (string): path to store any adsorbates flagged as
			problematic (defaults to /errors within the directory
			containing the starting CIF file)

		Returns:
			new_atoms (Atoms object): ASE Atoms object of MOF with adsorbate

			new_name (string): name of MOF with adsorbate
		"""
		#Check for file and prepare paths
		if not os.path.isfile(atoms_filepath):
			print('WARNING: No MOF found for '+atoms_filepath)
			return None, None
		if self.site_species is None and self.site_idx is None:
			raise ValueError('site_species or site_idx must be specified')

		if new_mofs_path is None:
			new_mofs_path = os.path.join(os.getcwd(),'new_mofs')
		if error_path is None:
			error_path = os.path.join(os.getcwd(),'errors')
		
		#Get ASE index of adsorption site
		site_species = self.site_species
		site_idx = self.site_idx
		if write_file:
			prep_paths(new_mofs_path,error_path)
		atoms = read(atoms_filepath)
		if site_idx is None:
			site_idx = [atom.index for atom in atoms if atom.symbol == 
			site_species][-1]

		#Get ASE indices of coordinating atoms and vectors from adsorption site
		neighbors_idx = get_NNs_pm(atoms,site_idx,NN_method)
		mic_coords = np.squeeze(atoms.get_distances(site_idx,neighbors_idx,
			mic=True,vector=True))

		#Get the optimal adsorption site
		ads_optimizer = ads_pos_optimizer(self,atoms_filepath,
					new_mofs_path=new_mofs_path,error_path=error_path)
		ads_pos = ads_optimizer.get_opt_ads_pos(mic_coords,site_idx)
		new_atoms, new_name = ads_optimizer.get_new_atoms_pm(ads_pos,site_idx)

		return new_atoms, new_name

	def get_adsorbate_oms(self,atoms_filepath,oms_data_path=None,
		oms_format='OMD',write_file=True,new_mofs_path=None,error_path=None):
		"""
		This function adds an adsorbate to each unique OMS in a given
		structure. In cases of multiple identical OMS, the adsorbate with
		fewest nearest neighbors is selected. In cases of the same number
		of nearest neighbors, the adsorbate with the largest minimum distance
		to extraframework atoms (excluding the adsorption site) is selected.

		Args:

			atoms_filepath (string): filepath to the CIF file

			oms_data_path (string): path to the data describing the OMS
			environments in either Zeo++ or OpenMetalDetector format (defaults
			to /oms_results within the directory containing the starting CIF file)

			oms_format (string): accepts either 'zeo' or 'OMD' for either a
			Zeo++-formatted .oms and .omsex file or OpenMetalDetector results
			(defaults to OMD)

			write_file (bool): if True, the new ASE atoms object should be
			written to a CIF file (defaults to True)
			
			new_mofs_path (string): path to store the new CIF files if
			write_file is True (defaults to /new_mofs within the directory
			containing the starting CIF file)
			
			error_path (string): path to store any adsorbates flagged as
			problematic (defaults to /errors within the directory
			containing the starting CIF file)

		Returns:
			new_atoms_list (list): list of ASE Atoms objects with an adsorbate
			added to each unique OMS
			
			new_name_list (list): list of names associated with each atoms
			object in new_atoms_list
		"""
		#Check for file and prepare paths
		if not os.path.isfile(atoms_filepath):
			print('WARNING: No MOF found for '+atoms_filepath)
			return None, None
		if oms_data_path is None:
			oms_data_path = os.path.join(os.path.dirname(atoms_filepath),'oms_results')
		if new_mofs_path is None:
			new_mofs_path = os.path.join(os.getcwd(),'new_mofs')
		if error_path is None:
			error_path = os.path.join(os.getcwd(),'errors')

		if write_file:
			prep_paths(new_mofs_path,error_path)

		#Get MOF name and read in as ASE atoms object
		atoms_filename = os.path.basename(atoms_filepath)
		name = get_refcode(atoms_filename)
		atoms = read(atoms_filepath)

		#Get OMS data
		oms_format = oms_format.lower()
		if oms_format == 'zeo':
			omsex_dict = get_zeo_data(oms_data_path,name,atoms)
		elif oms_format == 'omd':
			omsex_dict = get_omd_data(oms_data_path,name,atoms)
		else:
			raise ValueError('Unknown oms_format for '+oms_format)
		if omsex_dict is None:
			return None, None

		#Cycle through each open metal site
		cluster_sym = []
		for i, oms_idx in enumerate(omsex_dict['oms_idx']):

			#Get atomic numbers of OMS/NNs
			oms_atnum_temp = [atoms[oms_idx].number]
			NN_idx = omsex_dict['NN_idx'][i]
			if len(NN_idx) == 1:
				NN_atnum_temp = [atoms[NN_idx].number]
			else:
				NN_atnum_temp = atoms[NN_idx].get_atomic_numbers().tolist()
			NN_atnum_temp.sort()
			
			#Store stoichiometry of OMS and NNs
			cluster_sym.append(oms_atnum_temp+NN_atnum_temp)

		#Find only unique OMS environments
		unique_cluster_sym_all = []
		for entry in cluster_sym:
			if entry not in unique_cluster_sym_all:
				unique_cluster_sym_all.append(entry)

		#Cycle through each chemically unique OMS environment
		idx_counter = 0
		new_atoms_list = []
		new_name_list = []
		for unique_cluster_sym in unique_cluster_sym_all:

			omsex_indices = [idx for idx, entry in enumerate(cluster_sym)
				if entry == unique_cluster_sym]
			ads_positions = np.zeros((len(omsex_indices),3))

			#Cycle through each (chemically identical) OMS environment
			for i, omsex_idx in enumerate(omsex_indices):

				#Get Euclidean vectors for coordinating atoms with OMS at
				#the origin
				oms_idx = omsex_dict['oms_idx'][omsex_idx]
				NN_idx = omsex_dict['NN_idx'][omsex_idx]
				mic_coords = np.squeeze(atoms.get_distances(oms_idx,NN_idx,
					mic=True,vector=True))

				#Get adsorption sites
				ads_optimizer = ads_pos_optimizer(self,atoms_filepath,
					new_mofs_path=new_mofs_path,error_path=error_path)
				ads_positions[i,:] = ads_optimizer.get_opt_ads_pos(mic_coords,
					oms_idx)
				
			#Identify optimal adsorption site
			oms_idx_cluster = [omsex_dict['oms_idx'][j] for j in omsex_indices]
			best_to_worst_idx = ads_optimizer.get_best_to_worst_idx(ads_positions,
				oms_idx_cluster)

			#Get new atoms object with adsorbate
			new_atoms, new_name = ads_optimizer.get_new_atoms_auto_oms(
				ads_positions,best_to_worst_idx,unique_cluster_sym)

			new_atoms_list.append(new_atoms)
			new_name_list.append(new_name)
			idx_counter += len(omsex_indices)

		if idx_counter != len(omsex_dict['oms_sym']):
			raise ValueError('Did not run through all OMS')

		return new_atoms_list, new_name_list