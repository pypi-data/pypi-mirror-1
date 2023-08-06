"""Gaussian Network Model for study of protein dynamics.

Author:
    Ahmet Bakan
    http://www.pitt.edu/~ahb12
    
License:
    This Python package is distributed under GNU General Public License.

Classes:
    GNM
    GNMException
    
"""
import gzip
import logging
import os.path
import time

from Bio.KDTree import KDTree
from Bio.PDB import PDBParser

try:
    import matplotlib.pyplot as pl
except ImportError:
    PYLAB = False
else:
    PYLAB = True
    

import numpy as np
import scipy.linalg as la

PDB_PARSER = PDBParser()

def _str_to_lint(astr, sep=',', sep2='-'):
    """Returns a list of integers for a given structured string of numbers.
    
    Parameters
    ----------
    s : str
        Comma separated nonnegative integers. E.g. 3,6,7 or 3,7-10,12
    sep : str, optional
        Separator, which is by default ",".         
    sep2 : str, optional
        Separator 2, which is by default "-".
        
    """
    lint = []
    try:
        for items in astr.strip().split(sep):
            item = items.strip().split(sep2)
            if len(item) == 1:
                lint += [int(item[0])]
            elif len(item) == 2:
                lint += range(int(item[0]), int(item[1])+1)
            else:
                return False
    except (TypeError, ValueError):
        return False
    return lint

class GNMException(Exception):
    """GNM specific exceptions."""
    pass
    
class GNM(object):
    """A class for Gaussian Network Model calculations of proteins."""
    
    def __init__(self, pdbfile, verbose=True):
        """Initialize GNM for a protein structure in a PDB file.
        
        Parameters
        ----------
        pdbfile : str
            Path to a PDB file. Gzipped or zipped PDB files are also accepted.
            
        """
        if not os.path.isfile(pdbfile):
            raise GNMException('PDB file {0:s} is not a valid path.'
                               .format(pdbfile))
        self.name = os.path.split(pdbfile)[1].split('.')[0]
        self.pdbfile = pdbfile

        self.coordinates = None
        self.resids = None
        self.resnames = None
        self.chainids = None
        self.n_atoms = 0
        self.bfactors = None
        self._resids = None

        self.cutoff = 10.0
        self.gamma = 1.
        self.kirchhoff = None
        
        self._kdtree = None
        
        self.eigenvalues = None
        self.eigenvectors = None
        self._covariance = None
        self.n_modes = 0
        
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
    
        if verbose:
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            console.setFormatter(logging.Formatter('GNM: %(message)s'))
            self.logger.addHandler(console)


        if not PYLAB:
            self.logger.info('matplotlib was not found. Plotting functions '
                             'are not available.')
        
    def __repr__(self):
        return ('GNM of {0:s} (file: {1:s}) with {2:d} selected residues and '
                '{3:d} calculated modes (cutoff={4:.1f}A and gamma={5:.1f})'
                .format(self.name, self.pdbfile, self.n_atoms, self.n_modes,
                self.cutoff, self.gamma))
                
        
    def select_residues(self, selstr=None, model_index=0):
        """Select residues to be consired in GNM calculations.
        
        Parameters
        ----------
        selstr : str
            See examples below.
        model_index : int, optional
            If not specified, coordinates of the 1st (corresponding to index 0)
            model in the PDB file will be used.
        
        Selection Examples
        ------------------
        "*" and "*:*"
        select all chains and residues

        "A:x,y-z,w D:k-l G:*"
        select residues x, y to z (inclusive),
                    and w in chain A
        and residues k to l (inclusive) in chain D
        and all residues in chain G

        "A B"
        select all residues in chains A and B

        "*:5-25,50-100"
        select same set of residues in all chains
             
        """
        if self.pdbfile.endswith('gz'):
            pdbfile = gzip.open(self.pdbfile, 'r')
        else: 
            pdbfile = open(self.pdbfile, 'r')
        model = PDB_PARSER.get_structure(self.name, pdbfile).get_list()
        
        if (not isinstance(model_index, int) or 
            not 0 <= model_index < len(model)): 
            raise GNMException('Model index {0:s} is invalid.'
                               .format(str(model_index)))
        model = model[model_index]
        self.logger.info('Which chains and residues do you want to use '
                             'from {0:s}:'.format(self.name))
        chain_ids = []
        res_lists = []
        for chain in model.get_list():
            # NOTE: A whole bunch of code is omitted, since only residues
            # containing CA atoms are returned.
            chain_ids.append(chain.get_id())
            res_lists.append(chain.get_list())
            self.logger.info('\tChain {0:s} length {1:d} (Residue numbers '
                              'range from {2:d} to {3:d})' 
                              ''.format(chain_ids[-1], len(res_lists[-1]),
                                             res_lists[-1][0].get_id()[1], 
                                             res_lists[-1][-1].get_id()[1]))

        trial = 0
        all_residues = range(10000)
        while True:
            if selstr is None:
                if trial == 0:
                    self.logger.info(
                          'Please enter a selection based on these examples:\n'
                          '\n'
                          '\t "*" and "*:*"\n'
                          '\t   select all chains and residues\n'
                          '\n'
                          '\t "A:x,y-z,w D:k-l G:*"\n'
                          '\t   select residues x, y to z (inclusive),\n' 
                          '\t                and w in chain A\n'
                          '\t   and residues k to l (inclusive) in chain D\n'
                          '\t   and all residues in chain G\n'
                          '\n'
                          '\t "A B"\n'
                          '\t   select all residues in chains A and B\n'
                          '\n'
                          '\t "*:5-25,50-100"\n'
                          '\t   select same set of residues in all chains\n'
                          '\n'
                          '\tIf nothing is entered, no action will be taken.')
                selstr = raw_input('      Enter your selection: ').strip()
            else: 
                selstr = selstr.strip() 
            trial += 1
            # the case where nothing is entered
            if selstr == '':
                if trial == 1:
                    self.logger.info('You did not enter a selection. '
                                     'Would you like to try again?')
                    selstr = None
                    continue
                else:
                    self.logger.info('\tNothing is selected.')
                    return None
            self.logger.info('\tYou have entered: {0:s}'.format(selstr))
            
            # all needs to be done is filling in the following dict
            sel_dict = {}
            # the case where something is entered
            restart = False
            if selstr == '*':
                for chain_id in chain_ids:
                    sel_dict[chain_id] = all_residues
                break
            else:
                selstr_parts = selstr.split()
                # evaluate the case *:1-100,122
                if len(selstr_parts) == 1:
                    ch_sel = selstr_parts[0].split(':')
                    if len(ch_sel) == 2:
                        ch_id = ch_sel[0].strip().upper()
                        if ch_id == '*':
                            selstr_parts = []
                            for ch_id in chain_ids:
                                selstr_parts.append(ch_id+':'+ch_sel[1])
                        
                for ch_selstr in selstr_parts:
                    ch_sel = ch_selstr.split(':')
                    ch_id = ch_sel[0].strip().upper()
                    if not ch_id in chain_ids:
                        self.logger.info('\t{0:s} in {1:s} is not a valid '
                                         'chain id. Please try again.'
                                         .format(ch_id, ch_selstr))
                        restart = True
                        break
                    
                    if len(ch_sel) == 1:
                        ch_sel.append('*')
                    elif (len(ch_sel) > 2 or len(ch_sel[1].strip()) == 0):
                        self.logger.info('\t{0:s} is not understood. Please '
                                         'try again.'.format(ch_selstr))
                        restart = True
                        break

                    resid_str = ch_sel[1].strip()
                    if resid_str == '*':
                        sel_dict[ch_id] = all_residues
                    else:
                        resid_lint = _str_to_lint(resid_str)
                        if resid_lint:
                            if sel_dict.has_key(ch_id):
                                sel_dict[ch_id] += resid_lint
                            else:
                                sel_dict[ch_id] = resid_lint
                        else: 
                            self.logger.info('\t{0:s} in {1:s} is not '
                                             'understood. Please try again.'
                                             .format(resid_str, ch_selstr))
                            restart = True
                            break            
            if restart is True: 
                selstr = None
            else: break

        self.logger.info('Selection result:')
        start = time.time()
        self.coordinates = []
        self.resids = []
        self.resnames = []
        self.bfactors = []
        self.chainids = []
        for chain_id, res_list in zip(chain_ids, res_lists):
            if sel_dict.has_key(chain_id):
                count = 0
                sel_resids = sel_dict[chain_id] 
                for res in res_list:
                    if res.get_id()[1] in sel_resids:
                        if res.has_id('CA'):
                            calpha = res['CA']
                            count += 1
                            self.resids.append(res.get_id()[1])
                            self.resnames.append(res.get_resname())
                            self.coordinates.append(calpha.coord)
                            self.bfactors.append(calpha.bfactor)
                            self.chainids.append(chain_id)
                if count > 0:
                    self.logger.info('\t{0:d} residues from chain {1:s}'
                                     ''.format(count, chain_id))
                    self.n_atoms += count
        self.coordinates = np.array(self.coordinates, 'd')
        self._kdtree = KDTree(3)
        self._kdtree.set_coords(self.coordinates)
        self.bfactors = np.array(self.bfactors)
        
        ordered = True
        for i in range(1, self.n_atoms):
            if self.resids[i] <= self.resids[i-1]:
                ordered = False
                break
        if ordered:
            self._resids = np.array(self.resids)
        else:
            self._resids = np.arange(1, self.n_atoms+1)
            
        self.logger.info('Coordinate data was prepared in {0:.0f}ms.'
                          .format((time.time()-start)*1000))
            
    def set_kirchhoff(self, cutoff=10., gamma=1.):
        """Build Kirchhoff matrix for selected residues.
        
        Parameters
        ----------
        cutoff : float, optional
            If not specified, defailt value 10 A is used.
        gamma : float, optional
            If not specified, default value 1 is used.
             
        """
        if self.coordinates is None: 
            raise GNMException('Coordinates are not set. Run select_residues '
                               'method first.')
        start = time.time()
        self.logger.info('Kirchhoff matrix is being calculated.')
        self.logger.info('  Cutoff distance is set to {0:.2f}.'
                         .format(self.cutoff))
        self.logger.info('  Force constant is set to {0:.2f}.'
                         .format(self.gamma))
        self.cutoff = float(cutoff)
        self.gamma = float(gamma)
        
        self._kdtree.all_search(self.cutoff)
        self.kirchhoff = np.zeros((self.n_atoms, self.n_atoms), 'd')
        for res_i, res_j in self._kdtree.all_get_indices():
            self.kirchhoff[res_i, res_j] = -self.gamma
            self.kirchhoff[res_j, res_i] = -self.gamma
            self.kirchhoff[res_i, res_i] += self.gamma
            self.kirchhoff[res_j, res_j] += self.gamma
        self.logger.info('Kirchhoff matrix was calculated in {0:.0f}ms.'
                          .format((time.time()-start)*1000))
        
    def calculate_modes(self, n_modes=None):
        """Calculate normal modes by diagonalizing Kirchhoff matrix.
        
        Parameters
        ----------
        n_modes : float, optional
            Number of nonzero modes to calculate. Modes from the lower 
            frequency end of the mode spectrum will be calculated.
             
        """
        if self.kirchhoff is None: 
            raise GNMException('Kirchhoff matrix is not build. Run ' 
                               'set_kirchhoff method first.')
        start = time.time()
        self.logger.info('Normal modes are being calculated.')
        if n_modes: 
            eigvals = (0, n_modes)
            turbo = False
        else: 
            eigvals = None
            n_modes = self.n_atoms - 1
            turbo = True
        self.logger.info('  {0:d} modes will be calculated \n'
          '        (including mode with zero eigenvalue).'.format(n_modes + 1))
        self.eigenvalues, self.eigenvectors = la.eigh(self.kirchhoff, 
                                               turbo=turbo, eigvals=eigvals)
        self.n_modes = self.eigenvalues.shape[0]
        self.logger.info('Normal modes were calculated in {0:.0f}ms.'
                          ''.format((time.time()-start)*1000))
        
    def perform_analysis(self, cutoff=10., n_modes=20):
        """Build Kirchhoff matrix and calculate modes.
        
        Parameters
        ----------
        cutoff : float, optional
            If not specified, defailt value 10 A is used.
        n_modes : float, optional
            Number of nonzero modes to calculate. Modes from the lower 
            frequency end of the mode spectrum will be calculated.
            
        """
        if self.coordinates is None: 
            raise GNMException('Coordinates are not set. Run select_residues '
                               'method first.')
        self.set_kirchhoff(cutoff)
        self.calculate_modes(n_modes)
        
    def get_covariance(self, indices=None):
        """Return covariance matrix.
        
        Parameters
        ----------
        indices : array_like, optional
            When None is provided, covariance matrix is calculated based on 
            all available modes.
            If a list of integers is given, covariance matrix is calculated 
            using modes corresponding to the given indices.
            
        Example
        -------
        # Get covariance corresponding to nonzero lowest frequency 10 modes
        >>> gnm.get_covariance(range(1,1))
        
        """
        if indices is None:
            if self._covariance is None:
                self._covariance = np.dot(self.eigenvectors[:, 1:], 
                                        np.dot(np.diag(1/self.eigenvalues[1:]), 
                                               self.eigenvectors[:, 1:].T))
            return self._covariance
        else:
            return np.dot(self.eigenvectors[:, indices], 
                                 np.dot(np.diag(1/self.eigenvalues[indices]), 
                                        self.eigenvectors[:, indices].T))
            
    def get_cross_correlations(self, indices=None):
        """Return cross-correlations matrix.
        
        Parameters
        ----------
        indices : array_like, optional
            When None is provided, cross-correlations matrix is calculated 
            based on all available modes.
            If a list of integers is given, cross-correlations matrix is 
            calculated using modes corresponding to the given indices.
            
        Example
        -------
        # Get cross-correlations corresponding to nonzero lowest frequency 10 
        # modes
        >>> gnm.get_cross_correlations(range(1,1))
        
        """
        covariance = self.get_covariance(indices)
        diag = np.power(covariance.diagonal(), 0.5)
        return covariance / np.outer(diag, diag)
    
    def get_eigenvalues(self, indices=None):
        """Return eigenvalues at given indices.
        
        Parameters
        ----------
        indices : array_like, optional
            If None, all eigenvalues will be returned.
        
        """
        if indices is None:
            indices = range(self.n_modes)
        return self.eigenvalues[indices]

    def get_eigenvectors(self, indices=None):
        """Return eigenvectors at given indices.
        
        Parameters
        ----------
        indices : array_like, optional
            If None, all eigenvectors will be returned.
        
        """
        if indices is None:
            indices = range(self.n_modes)
        return self.eigenvectors[:, indices]
    
    def get_modes(self, indices=None):
        """Return GNM mode (squared eigenvector) at given indices.
        
        Parameters
        ----------
        indices : array_like, optional
            If None, all modes will be returned.
            
        """
        if indices is None:
            indices = range(self.n_modes)
        return self.eigenvectors[:, indices]**2
    
    def get_square_fluctuations(self, indices=None):
        """Return square-fluctuations along selected modes.
        
        Eigenvalue weighted sum of square-fluctuations along selected modes
        is returned.
        
        Parameters
        ----------
        indices : array_like, optional
            If None, all modes will be used to calculate square-fluctuations.
        
        """
        if indices is None:
            indices = range(1, self.n_modes)
        return np.dot(self.eigenvectors[:, indices]**2, 
                      1 / self.eigenvalues[indices])
    
    if PYLAB:
        def plot_eigenvector(self, index, *args, **kwargs):
            """Plot eigenvector at a given index.
            
            Arguments and keyword arguments following index are directly passed
            to plot function in matplotlib.
            
            """
            pl.plot(self._resids, self.eigenvectors[:, index], *args, **kwargs)
            pl.title('GNM eigenvector {0:d} for {1:s}'.format(index, 
                                                              self.name))
            pl.xlabel('Residue numbers')
            pl.ylabel('GNM eigenvector {0:d}'.format(index))
            pl.grid()

        def plot_mode(self, index, *args, **kwargs):
            """Plot mode at a given index.
            
            Arguments and keyword arguments following index are directly passed
            to plot function in matplotlib.
            
            """
            pl.plot(self._resids, self.eigenvectors[:, index]**2, 
                    *args, **kwargs)
            pl.title('GNM mode {0:d} for {1:s}'.format(index, self.name))
            pl.xlabel('Residue numbers')
            pl.ylabel('GNM mode {0:d}'.format(index))
            pl.grid()

            
        def plot_bfactors(self, *args, **kwargs):
            """Plot experimental beta factors parsed from PDB file.
            
            Arguments and keyword arguments following index are directly passed
            to plot function in matplotlib.
            
            """
            pl.plot(self._resids, self.bfactors, *args, **kwargs)
            pl.title('Beta-factors for {0:s}'.format(self.name))
            pl.xlabel('Residue numbers')
            pl.ylabel('Beta-factors')
            pl.grid()

        def plot_square_fluctuations(self, indices=None, *args, **kwargs):
            """Plot square-fluctuations calculated using specified modes.
            
            Arguments and keyword arguments following index are directly passed
            to plot function in matplotlib.
            
            Parameters
            ----------
            indices : array_like, optional
                If None, all modes will be used to calculate 
                square-fluctuations.
            
            """
            if indices is None:
                howmany = 'all'
            else:
                if isinstance(indices, int):
                    howmany = '1'
                else:
                    howmany = str(len(indices))
            pl.plot(self._resids, self.get_square_fluctuations(indices), 
                    *args, **kwargs)
            pl.title('GNM square-fluctuations for {0:s} using {1:s} modes'
                     .format(self.name, howmany))
            pl.xlabel('Residue numbers')
            pl.ylabel('Square-fluctuations')
            pl.grid()
            
        def show_cross_correlations(self, indices=None, *args, **kwargs):
            """Show cross-correlations matrix.
            
            Parameters
            ----------
            indices : array_like, optional
                When None is provided, cross-correlations matrix is calculated 
                based on all available modes.
                If a list of integers is given, cross-correlations matrix is 
                calculated using modes corresponding to the given indices.
            """
            if indices is None:
                howmany = 'all'
            else:
                if isinstance(indices, int):
                    howmany = '1'
                else:
                    howmany = str(len(indices))
            cross_correlations = self.get_cross_correlations(indices)
            pl.imshow(cross_correlations, *args, origin='lower', **kwargs)
            pl.colorbar()
            pl.title('GNM cross-correlations for {0:s} using {1:s} modes'
                     .format(self.name, howmany))
            
    def write_pdb(self, filename=None, bfactors=None):
        """Write alpha-carbon only PDB file.
        
        Bfactor column of PDB will contain GNM square-fluctuations calculated
        using specified modes.
        
        Parameters
        ----------
        filename : str, optional
            Output filename. If none is given name_gnm.pdb will be used.
        bfactor : array_like, optional
            Is not provided, square-fluctuations will be written on 
            beta-column.
        """
        if bfactors is None:
            bfactors = self.get_square_fluctuations()
        if filename is None:
            filename = self.name + '_gnm.pdb'
        pdb = open(filename, 'w')
        for i in range(self.n_atoms):
            xyz = self.coordinates[i]
            pdb.write('{0:6s}{1:5d}{2:2s}{3:3s}{4:1s}{5:4s}{6:1s}{7:4d}'
                      '{8:4s}{9:8.3f}{10:8.3f}{11:8.3f}{12:6.2f}{13:6.2f}\n'
                      .format('ATOM  ', i+1, '  ', 'CA'.ljust(3), ' ', 
                      self.resnames[i].ljust(4), self.chainids[i], 
                      self.resids[i], '    ', xyz[0], xyz[1], xyz[2], 1.0, 
                      bfactors[i]))
        pdb.close()
        self.logger.info('Coordinates and square-fluctuations are written'
                         'into {0:s}.'.format(filename))