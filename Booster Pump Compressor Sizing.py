# code to find the input flow rates needed to run the booster pump

import pint
from CoolProp.CoolProp import PropsSI
ureg = pint.UnitRegistry()

# inputs
fluid = 'helium'
fluid2 = 'air'
COPV_vol = 18.1     *(ureg.liter)
temp_He = 297     *(ureg.K)

# in order to find maximum and minimum air compressor flow rate needed, I first need the inlet pressures (mostly at the start and end of the pump runtime)
# min inlet pressure is 200 psig   max inlet pressure is 9000 psig
# min air pressure is 20 psig   max air pressur is 150 psig
#pressure ratio of the pump is 62:1  which is discharge:inlet

fillTank_vol = 42.2    *(ureg.liter)
fillTank_p = 6000      *(ureg.psi)
full_COPV_P = 4935   *(ureg.psi)
air_p = 100    *(ureg.psi)

print('\n-----Initial condions-----\n')

comp_fact = PropsSI('Z', 'P', full_COPV_P.to(ureg.Pa).magnitude, 'T', temp_He.magnitude, fluid)  # finding compressibility factor, not really useful for this code
print(f"The compressibility factor of helium is {comp_fact:.2f}")

density_He_COPV = PropsSI('D', 'P', full_COPV_P.to(ureg.Pa).magnitude, 'T', temp_He.magnitude, fluid)   *((ureg.kg) / (ureg.m)**3)  # density of heluim inside the copv
print(f"The density of the helium in the tank is {density_He_COPV:.2f}")

density_air = PropsSI('D', 'P', air_p.to(ureg.Pa).magnitude, 'T', temp_He.magnitude, fluid2)   *((ureg.kg) / (ureg.m)**3)  # density of the air being supplied to the pump
print(f"The density of air is {density_air:.2f}")

density_HE_fill = PropsSI('D', 'P', fillTank_p.to(ureg.Pa).magnitude, 'T', temp_He.magnitude, fluid)   *((ureg.kg) / (ureg.m)**3)  # density of the helium inside the fill tanks (at the starting pressure)

# static outlet pressure is equal to 60 * (air pressure) + gas pressure
# 5000 psig = 60 * (air_p) + gas pressure   where gas pressure is changing

print('\n\n-----Finding the range of conditions the pump must run in-----\n')

totalMass_He = density_He_COPV * COPV_vol  # the total mass of heluim needed to fill the copv
print(f"The total mass of helium need to fill the COPV is {totalMass_He.to_base_units():.4f}")

mass_He_fill = density_HE_fill * fillTank_vol  # intital mass of the helium inside the fill tank 
print(f"The mass of helium in the fill tank is {mass_He_fill.to_base_units():.4f}")

equal_den = mass_He_fill / (COPV_vol + fillTank_vol)    # finds the density of helium when the tanks are at equilibrium
equal_p = PropsSI('P', 'D', equal_den.magnitude, 'T', temp_He.magnitude, fluid)    *(ureg.Pa) # uses density at equilibrium to find the equilization pressure
print(f"The equalization pressure of the system is {equal_p.to(ureg.psi):.2f}")  # equalization pressure is around 3980 psi, the leftover 1000 psi is laft to the booster to fill

# will most likely find scfm need by the pump by using the chamber volume and the actuations per minute

He_p = equal_p         # the heluim inlet pressure to the pump (will change with time)
boost_p = 60 * air_p + He_p
print(f"The boosted pressure is {boost_p:.2f}")        # maximum pressure rating of the copv is 340 bar or 4935 psi

min_fillTank_d = (mass_He_fill - totalMass_He) / fillTank_vol   # the minimum density of heluim inside the fill tank (when the copv is full), will use as a maximum boost pressure needed to generate
min_fillTank_p = PropsSI('P', 'D', min_fillTank_d.magnitude, 'T', temp_He.magnitude, fluid)   *(ureg.Pa)
print(f"The minimum tank pressure is {min_fillTank_p.to(ureg.psi):.4f}")

max_boost_p = 60 * air_p + min_fillTank_p  # maximum predicted poost pressure expected
print(f"The maximum boost pressure is {max_boost_p.to(ureg.psi):.4f}")

mass_He_neededBoost = mass_He_fill - totalMass_He
print(f"The mass of helium need to be boosted by the pump is {mass_He_neededBoost.to_base_units():.4f}")

print('-----Air flowrate calculations-----')

# right now i am assuming the cyclic rate is can only be controlled by changing air volumetric flow rate or the air pressure, for now I want to keep the air pressure constant
pump_vol = 6.2   *(ureg.inch)**3   # displacement of the pistion per a cycle
# maximum cyclic rate is 60 cycles/min
# can find cyclic rate by finding piston velicity using piston area and pressure  --> need to contact representative form haskle for that info