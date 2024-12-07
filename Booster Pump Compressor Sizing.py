# code to find the input flow rates needed to run the booster pump

import pint
from CoolProp.CoolProp import PropsSI
ureg = pint.UnitRegistry()

# constant condtions
fluid = 'helium'
fluid2 = 'air'
COPV_vol = 18.1     *(ureg.liter)
temp_system = 297       *(ureg.K)

# in order to find maximum and minimum air compressor flow rate needed, I first need the inlet pressures (mostly at the start and end of the pump runtime)
#pressure ratio of the pump is 62:1  which is discharge:inlet

fillTank_vol = 42.2           *(ureg.liter)       # the volume of the fill tanks
start_fillTank_p = 6000             *(ureg.psi)         # the pressure of the fill tanks
full_COPV_P = 4935            *(ureg.psi)         # the final pressur of the copv
airDrive_p = 100              *(ureg.psi)         # pressure of the air drive gas, or the pressure that is supplied by the pump
driveChamber_vol = 6.2        *(ureg.inch)**3     # the volume of the drive gas chamber
driveChamber_stroke = 14.567  *(ureg.inch) # temporary placeholder
gasChamber_vol = 0.1            *(ureg.inch)**3  # temporary placeholder

# inputs
cfm_air = 60   *((ureg.feet)**3 / (ureg.min))

print('\n-----Initial condions-----\n')

comp_fact = PropsSI('Z', 'P', full_COPV_P.to(ureg.Pa).magnitude, 'T', temp_system.magnitude, fluid)  # finding compressibility factor, not really useful for this code
print(f"The compressibility factor of helium is {comp_fact:.2f}")

density_He_fullCOPV = PropsSI('D', 'P', full_COPV_P.to(ureg.Pa).magnitude, 'T', temp_system.magnitude, fluid)   *((ureg.kg) / (ureg.m)**3)  # density of heluim inside the copv
print(f"The density of the helium in the COPV when full is {density_He_fullCOPV:.2f}")

density_airDrive = PropsSI('D', 'P', airDrive_p.to(ureg.Pa).magnitude, 'T', temp_system.magnitude, fluid2)   *((ureg.kg) / (ureg.m)**3)  # density of the air being supplied to the pump
print(f"The density of air drive gas is {density_airDrive:.2f}")

density_HE_fill = PropsSI('D', 'P', start_fillTank_p.to(ureg.Pa).magnitude, 'T', temp_system.magnitude, fluid)   *((ureg.kg) / (ureg.m)**3)  # density of the helium inside the fill tanks (at the starting pressure)

# static outlet pressure is equal to 60 * (air pressure) + gas pressure
# 5000 psig = 60 * (air_p) + gas pressure   where gas pressure is changing

print('\n\n-----Finding equalization pressure-----\n')

totalMass_He = density_He_fullCOPV * COPV_vol  # the total mass of heluim needed to fill the copv
print(f"The total mass of helium need to fill the COPV is {totalMass_He.to_base_units():.4f}")

mass_He_fill = density_HE_fill * fillTank_vol  # intital mass of the helium inside the fill tank 
print(f"The mass of helium in the fill tank is {mass_He_fill.to_base_units():.4f}")

equal_den = mass_He_fill / (COPV_vol + fillTank_vol)    # finds the density of helium when the tanks are at equilibrium
equal_p = PropsSI('P', 'D', equal_den.magnitude, 'T', temp_system.magnitude, fluid)    *(ureg.Pa) # uses density at equilibrium to find the equilization pressure
print(f"The equalization pressure of the system is {equal_p.to(ureg.psi):.2f}")  # equalization pressure is around 3980 psi, the leftover 1000 psi is laft to the booster to fill

print('\n\n-----Finding the end condtions-----\n')

min_fillTank_d = (mass_He_fill - totalMass_He) / fillTank_vol   # the minimum density of heluim inside the fill tank (when the copv is full), will use as a maximum boost pressure needed to generate
min_fillTank_p = PropsSI('P', 'D', min_fillTank_d.magnitude, 'T', temp_system.magnitude, fluid)   *(ureg.Pa)
print(f"The minimum tank pressure is {min_fillTank_p.to(ureg.psi):.4f}")

max_boost_p_delt = full_COPV_P - min_fillTank_p
print(f"The maximum pressure boost amount is {max_boost_p_delt:.2f}")

max_boost_p = 60 * airDrive_p + min_fillTank_p  # maximum predicted poost pressure expected
print(f"The maximum boost pressure is {max_boost_p.to(ureg.psi):.4f}")

mass_He_neededBoost = mass_He_fill - totalMass_He
print(f"The mass of helium need to be boosted by the pump is {mass_He_neededBoost.to_base_units():.4f}")

print('\n\n-----Finding run time-----\n')

# must find piston speed first
airDrive_p = airDrive_p.to(ureg.Pa)
std_p = 1    *(ureg.atm)
std_p = std_p.to(ureg.Pa)
std_t = 273.15   *(ureg.K)

# right now assuming the temperature of the air drive gas is at standard temp
scfm_air = (cfm_air.magnitude / comp_fact) * (airDrive_p.magnitude / std_p.magnitude)  *((ureg.feet)**3 / (ureg.min))
print(f"The scfm into the pump is {scfm_air:.2f}")



# variables for calculations  (everything will be metric)
equal_p = equal_p.to(ureg.Pa)
COPV_p = equal_p.magnitude
print(f"------{COPV_p}")
fillTank_p = equal_p.magnitude
chamber_temp = temp_system.magnitude
time = 0   *(ureg.s)  # time in seconds
comp_time = 0
vol_flowRate = cfm_air.to((ureg.m)**3 / (ureg.second))
mass_flowRate = vol_flowRate * density_airDrive
print(f"The mass flow rate of air into the pump is {mass_flowRate:.5f}")



air_R_val = 287.05   *((ureg.J) / ((ureg.kg) * (ureg.K)))
He_R_val = 2077.1    *((ureg.J) / ((ureg.kg) * (ureg.K)))

vol_speed = mass_flowRate * air_R_val * temp_system / airDrive_p   # change in volume
print(f"The change in volume is {vol_speed.to_base_units():.5f}")

piston_area = driveChamber_vol.to_base_units() / driveChamber_stroke.to_base_units()

piston_speed = vol_speed / piston_area
print(f"The speed of the piston is {piston_speed.to_base_units():.3f}")


# maybe ask for isentropic efficiency
# comVol is the volume that is being compressed, massInVol is the mass of gas in the vloume, volSpeed is the rate of change of the volume
# stopP is the pressure at which the compression stops at, startP is the pressure the compression starts at, startTemp is the starting temp of the volume
# returns the time it takes to compress to a certian point, and the temperature after this compression
def compTimeCalc(compVol, volSpeed, stopP, startP, startTemp):   # calculates the time a compression takes  refrences nasa page on isentropic compression
    cp_air = PropsSI('CPMASS', 'P', startP, 'T', startTemp, 'helium')
    cv_air = PropsSI('CVMASS', 'P', startP, 'T', startTemp, 'helium')
    gamma = cp_air / cv_air

    new_temp = startTemp * (stopP / startP)**((gamma - 1) / gamma)
    stop_vol = compVol * (COPV_p / fillTank_p)**(-1 / gamma)
    delta_v = compVol - stop_vol
    compTime = delta_v / volSpeed
    return new_temp, compTime


# using: T2 / T1 = (p2 / p1) ^ [(gamma - 1)/gamma]
#cp_air = PropsSI('CPMASS', 'P', fillTank_p.magnitude, 'T', chamber_temp.magnitude, fluid)
#cv_air = PropsSI('CVMASS', 'P', fillTank_p.magnitude, 'T', chamber_temp.magnitude, fluid)
#gamma = cp_air / cv_air

#new_temp = chamber_temp * (COPV_p / fillTank_p)**((gamma - 1) / gamma)

#input_He_den = PropsSI('D', 'P', fillTank_p.to(ureg.Pa).magnitude, 'T', chamber_temp.magnitude, fluid2)   *((ureg.kg) / (ureg.m)**3)
#mass_in_vol = input_He_den * gasChamber_vol

#stop_vol = gasChamber_vol * (COPV_p / fillTank_p)**(-1 / gamma)
#print(stop_vol)
#delta_v = gasChamber_vol - stop_vol
#time = time + delta_v / vol_speed
#print(time)

chamber_temp, comp_time = compTimeCalc(gasChamber_vol.magnitude, vol_speed.magnitude, COPV_p, fillTank_p, chamber_temp)
print(chamber_temp)
print(comp_time)