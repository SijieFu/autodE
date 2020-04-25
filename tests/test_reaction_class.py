import os
from autode import reaction
from autode.transition_states.transition_state import TransitionState
from autode.bond_rearrangement import BondRearrangement
from autode.transition_states.ts_guess import TSguess
from autode.complex import ReactantComplex, ProductComplex
from autode.atoms import Atom
from autode.exceptions import UnbalancedReaction
from autode.exceptions import SolventsDontMatch
from autode.units import KcalMol
from autode.mol_graphs import make_graph
from autode.config import Config
import shutil
import pytest

here = os.path.dirname(os.path.abspath(__file__))

h1 = reaction.Reactant(name='h1', atoms=[Atom('H', 0.0, 0.0, 0.0)])

h2 = reaction.Reactant(name='h2', atoms=[Atom('H', 1.0, 0.0, 0.0)])
h2_product = reaction.Product(name='h2', atoms=[Atom('H', 1.0, 0.0, 0.0)])

lin_h3 = reaction.Reactant(name='h3_linear', atoms=[Atom('H', -1.76172, 0.79084, -0.00832),
                                                    Atom('H', -2.13052, 0.18085, 0.00494),
                                                    Atom('H', -1.39867, 1.39880, -0.00676)])

trig_h3 = reaction.Product(name='h3_trigonal', atoms=[Atom('H', -1.76172, 0.79084, -0.00832),
                                                      Atom('H', -1.65980, 1.15506, 0.61469),
                                                      Atom('H', -1.39867, 1.39880, -0.00676)])


def test_reaction_class():
    h1 = reaction.Reactant(name='h1', atoms=[Atom('H', 0.0, 0.0, 0.0)])
    hh_product = reaction.Product(name='hh', atoms=[Atom('H', 0.0, 0.0, 0.0), Atom('H', 0.7, 0.0, 0.0)])

    # h + h > mol
    hh_reac = reaction.Reaction(mol1=h1, mol2=h2, mol3=hh_product, name='h2_assoc')

    h1.energy = 2
    h2.energy = 3
    hh_product.energy = 1

    assert hh_reac.type == reaction.reactions.Dissociation
    assert len(hh_reac.prods) == 2
    assert len(hh_reac.reacs) == 1
    assert hh_reac.ts is None
    assert hh_reac.tss is None
    assert hh_reac.name == 'h2_assoc'
    assert hh_reac.calc_delta_e() == KcalMol.conversion * 4

    h1 = reaction.Reactant(name='h1', atoms=[Atom('H', 0.0, 0.0, 0.0)])
    hh_reactant = reaction.Reactant(name='hh', atoms=[Atom('H', 0.0, 0.0, 0.0), Atom('H', 1.0, 0.0, 0.0)])
    hh_product = reaction.Product(name='hh', atoms=[Atom('H', 0.0, 0.0, 0.0), Atom('H', 1.0, 0.0, 0.0)])

    # h + mol > mol + h
    h_sub = reaction.Reaction(mol1=h1, mol2=hh_reactant, mol3=h2_product, mol4=hh_product, solvent_name='water')

    assert h_sub.type == reaction.reactions.Substitution
    assert h_sub.name == 'reaction'
    assert h_sub.solvent.name == 'water'
    assert h_sub.solvent.smiles == 'O'


def test_check_rearrangement():

    # Linear H3 -> Trigonal H3
    make_graph(species=trig_h3, allow_invalid_valancies=True)
    reac = reaction.Reaction(lin_h3, trig_h3)

    # Should switch reactants and products if the products have more bonds than the reactants
    assert reac.reacs[0].name == 'h3_trigonal'
    assert reac.prods[0].name == 'h3_linear'


def test_reaction_identical_reac_prods():
    os.chdir(os.path.join(here, 'data'))

    hh_reactant = reaction.Reactant(name='hh', atoms=[Atom('H', 0.0, 0.0, 0.0), Atom('H', 1.0, 0.0, 0.0)])
    hh_product = reaction.Product(name='hh', atoms=[Atom('H', 0.0, 0.0, 0.0), Atom('H', 1.0, 0.0, 0.0)])

    h2_reaction = reaction.Reaction(hh_reactant, hh_product)

    h2_reaction.locate_transition_state()
    assert h2_reaction.ts is None

    shutil.rmtree('transition_states')
    os.chdir(here)


def test_bad_balance():

    hh_product = reaction.Product(name='hh', atoms=[Atom('H', 0.0, 0.0, 0.0), Atom('H', 1.0, 0.0, 0.0)])

    with pytest.raises(UnbalancedReaction):
        reaction.Reaction(mol1=h1, mol2=hh_product)

    h_minus = reaction.Reactant(name='h1_minus', atoms=[Atom('H', 0.0, 0.0, 0.0)], charge=-1)
    with pytest.raises(UnbalancedReaction):
        reaction.Reaction(h1, h_minus, hh_product)

    h1_water = reaction.Reactant(name='h1', atoms=[Atom('H', 0.0, 0.0, 0.0)], solvent_name='water')
    h2_water = reaction.Reactant(name='h2', atoms=[Atom('H', 1.0, 0.0, 0.0)], solvent_name='water')
    hh_thf = reaction.Product(name='hh', atoms=[Atom('H', 0.0, 0.0, 0.0), Atom('H', 1.0, 0.0, 0.0)], solvent_name='thf')

    with pytest.raises(SolventsDontMatch):
        reaction.Reaction(h1_water, h2_water, hh_thf)


def test_calc_delta_e():

    r1 = reaction.Reactant(name='h', atoms=[Atom('H', 0.0, 0.0, 0.0)])
    r1.energy = -0.5

    r2 = reaction.Reactant(name='h', atoms=[Atom('H', 0.0, 0.0, 0.0)])
    r2.energy = -0.5

    tsguess = TSguess(atoms=None, reactant=ReactantComplex(r1), product=ProductComplex(r2))
    tsguess.bond_rearrangement = BondRearrangement()
    ts = TransitionState(tsguess)
    ts.energy = -0.8

    p = reaction.Product(name='hh', atoms=[Atom('H', 0.0, 0.0, 0.0), Atom('H', 1.0, 0.0, 0.0)])
    p.energy = -1.0

    reac = reaction.Reaction(r1, r2, p)
    reac.ts = ts

    assert -1E-6 < reac.calc_delta_e() < 1E-6
    assert 0.2 - 1E-6 < reac.calc_delta_e_ddagger() / KcalMol.conversion < 0.2 + 1E-6


def test_solvated_reaction():
    os.chdir(os.path.join(here, 'data'))

    Config.lcode = 'xtb'
    Config.n_cores = 1
    Config.XTB.path = here       # A path that exists
    Config.ORCA.path = here       # A path that exists

    r = reaction.SolvatedReaction(lin_h3, trig_h3, solvent_name='water')
    assert r.solvent_mol is None

    r.calc_solvent()
    assert isinstance(r.solvent_mol, reaction.SolvatedMolecule)
    assert r.solvent_mol.energy == -3819.765189588065
    assert all(isinstance(mol, reaction.SolvatedMolecule) for mol in r.reacs + r.prods)

    os.remove('solvent/water_conf0_opt_xtb.xyz')
    os.remove('solvent/water_opt_orca.inp')
    os.remove('solvent/water_optimised_orca.xyz')
    os.remove('solvent/water_sp_orca.inp')
    os.remove('solvent/water_sp_orca.pc')
    os.chdir(here)