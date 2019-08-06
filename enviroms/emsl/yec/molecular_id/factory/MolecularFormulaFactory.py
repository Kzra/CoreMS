from copy import deepcopy
from enviroms.emsl.yec.mass_spectrum.calc.MolecularFormulaCalc import MolecularFormulaCalc
from enviroms.emsl.yec.encapsulation.settings.input.ProcessingSetting import MassSpecPeakSetting
from enviroms.emsl.yec.encapsulation.constant.Constants import Atoms


__author__ = "Yuri E. Corilo"
__date__ = "Jun 24, 2019"

class MolecularFormula(MolecularFormulaCalc):
    '''
    classdocs
    '''
    def __init__(self, _d_molecular_formula, ion_charge, exp_mz=None):
        
        #clear dictionary of atoms with 0 value
        self._d_molecular_formula = {key:val for key, val in _d_molecular_formula.items() if val != 0}
        self._ion_charge = ion_charge
        self._assigment_mass_error = None
        self._confidence_score = None
        self.is_isotopologue = False
        
        kendrick_dict_base = MassSpecPeakSetting.kendrick_base
        self._kdm, self._kendrick_mass, self._nominal_km = self._calc_kdm(
            kendrick_dict_base)  

        if exp_mz:
            self._assigment_mass_error = self._calc_assigment_mass_error(exp_mz)
            #self._confidence_score = self._calc_confidence_score()     
        
    def __len__(self):
        
        #crash if keys are not ordered
            return len(self._d_molecular_formula.keys())
        
    def __getitem__(self, atom):
        
            #atom = list(self._d_molecular_formula.keys())[position]
            return self._d_molecular_formula[atom]

    @property
    def O_C(self): return self._d_molecular_formula.get("O")/self._d_molecular_formula.get("C")
    
    @property
    def H_C(self): return self._d_molecular_formula.get("H")/self._d_molecular_formula.get("C")
    
    @property
    def dbe(self): return self._calc_dbe()
    
    @property
    def mz_nominal_theo(self): return int(self._calc_mz_theor())

    @property    
    def mz_error(self): return self._assigment_mass_error
    
    @property
    def mz_theor(self): return self._calc_mz_theor()

    @property
    def ion_type(self): return self._d_molecular_formula.get("IonType")
    
    @property
    def ion_charge(self): return self._ion_charge
    
    @property
    def atoms(self): return [key for key in self._d_molecular_formula.keys() if key != 'IonType']
    
    @property
    def confidence_score(self): return self._calc_confidence_score() 
        
    @property
    def kmd(self): return self._kdm

    @property
    def kendrick_mass(self): return self._kendrick_mass

    @property
    def knm(self): return self._nominal_km

    def change_kendrick_base(self, kendrick_dict_base):
        '''kendrick_dict_base = {"C": 1, "H": 2}'''
        self._kdm, self._kendrick_mass, self._nominal_km = self._calc_kdm(
            kendrick_dict_base)
                
    def isotopologues(self, min_abudance, current_abundance): 
        
        for mf in self._cal_isotopologues(self._d_molecular_formula, min_abudance, current_abundance ):

            yield MolecularFormulaIsotopologue(*mf, self.ion_charge)
    
    def atoms_qnt(self,atom): 
        if atom in self._d_molecular_formula:
            return self._d_molecular_formula.get(atom)
        else:
            raise Warning('Could not find %s in this Molecular Formula object'%str(atom))
    
    def atoms_symbol(self, atom): 
        '''return the atom symbol without the mass number'''
        return ''.join([i for i in atom if not i.isdigit()])

    @property       
    def to_string(self):
        
        if self._d_molecular_formula:
            
            formulalist = self.to_list
            
            formulastring = "" 
            
            for each in range(0, len(formulalist),2):
                
                formulastring = formulastring + str(formulalist[each]) + str(formulalist[each+1]) + " "    
                
            return formulastring[0:-1]   
       
        else:
            
            raise Exception("Molecular formula identification not performed yet")    
    
    @property
    def to_dict(self):
        return self._d_molecular_formula
    
    @property   
    def to_list(self):
        
        if self._d_molecular_formula:
            atoms_in_ordem = ["C", "H", "N", "O", "S", "P"]
    
            formula_list = []
            
            for atomo in atoms_in_ordem:
    
                numero_atom = self._d_molecular_formula.get(atomo)
    
                if numero_atom:
                    
                    formula_list.append(atomo)
                    formula_list.append(numero_atom)
                #else:
                #    formula_list_zero_filled.append(atomo)
                #    formula_list_zero_filled.append(0)
    
            atomos_in_dict = self._d_molecular_formula.keys()
            for atomo in atomos_in_dict:
    
                if atomo not in atoms_in_ordem and atomo != "IonType":
                    
                    formula_list.append(atomo)
                    formula_list.append(self._d_molecular_formula.get(atomo))
    
            return formula_list
        else:
            raise Exception("Molecular formula identification not performed yet")
        
    @property
    def class_label(self):
        
        if self._d_molecular_formula:
            
            formulalist = self.to_list
            classstring = "" 
            
            for each in range(0, len(formulalist),2):
                
                if formulalist[each] != 'C' and formulalist[each] != 'H':
                     
                    classstring = classstring + str(formulalist[each]) + str(formulalist[each+1]) + " "    
            
            if classstring == "": classstring = "HC "
                
            if self._d_molecular_formula.get("IonType") == 'RADICAL':    
                
                return classstring[0:-1] + " " + "-R"
            
            else: return classstring[0:-1] + " "
            
            'dict, tuple or string'
        else:
            raise Exception("Molecular formula identification not performed yet")        
    
    

class MolecularFormulaIsotopologue(MolecularFormula):
        
    '''
    classdocs
    '''
    def __init__(self, _d_molecular_formula, prop_ratio, ion_charge, exp_mz=None):
        
        super().__init__(_d_molecular_formula,  ion_charge)
        #prop_ratio is relative to the monoisotopic peak p_isotopologue/p_mono_isotopic
        self.prop_ratio = prop_ratio
        
        self.is_isotopologue = True
        
        if exp_mz:
            
            self._assigment_mass_error = self._calc_assigment_mass_error(exp_mz)
            self._confidence_score = False