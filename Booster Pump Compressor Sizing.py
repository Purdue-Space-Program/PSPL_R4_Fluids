# code to find the time it takes to fully fill the COPV with a given input flow rate

import pint
from CoolProp.CoolProp import PropsSI
ureg = pint.UnitRegistry()

# constant variables
COPV_vol = 18.1               *(ureg.liter)       # vloume of the COPV
temp_system = 297             *(ureg.K)           # the ambient temperature
fillTank_vol = 42.2           *(ureg.liter)       # the volume of the fill tanks
start_fillTank_p = 6000       *(ureg.psi)         # the pressure of the fill tanks
full_COPV_P = 4935            *(ureg.psi)         # the final pressure of the copv
airDrive_p = 100              *(ureg.psi)         # pressure of the air drive gas, or the pressure that is supplied by the pump
driveChamber_vol = 6.2        *(ureg.inch)**3     # the volume of the drive gas chamber
driveChamber_stroke = 14.567  *(ureg.inch) # temporary placeholder
gasChamber_vol = 0.1            *(ureg.inch)**3  # temporary placeholder

# inputs
cfm_air = 10   *((ureg.feet)**3 / (ureg.min))   # the volumetric flow rate (cfm)


print('\n-----Initial condions-----\n')

comp_fact = PropsSI('Z', 'P', airDrive_p.to(ureg.Pa).magnitude, 'T', temp_system.magnitude, 'helium')  # finding compressibility factor, not really useful for this code
print(f"The compressibility factor of the air drive is {comp_fact:.2f}")

density_He_fullCOPV = PropsSI('D', 'P', full_COPV_P.to(ureg.Pa).magnitude, 'T', temp_system.magnitude, 'helium')   *((ureg.kg) / (ureg.m)**3)  # density of heluim inside the copv
print(f"The density of the helium in the COPV when full is {density_He_fullCOPV:.2f}")

density_airDrive = PropsSI('D', 'P', airDrive_p.to(ureg.Pa).magnitude, 'T', temp_system.magnitude, 'air')   *((ureg.kg) / (ureg.m)**3)  # density of the air being supplied to the pump
print(f"The density of air drive gas is {density_airDrive:.2f}")

density_HE_fill = PropsSI('D', 'P', start_fillTank_p.to(ureg.Pa).magnitude, 'T', temp_system.magnitude, 'helium')   *((ureg.kg) / (ureg.m)**3)  # density of the helium inside the fill tanks (at the starting pressure)


print('\n\n-----Finding equalization pressure-----\n')

totalMass_COPV = density_He_fullCOPV * COPV_vol  # the total mass of heluim needed to fill the copv
print(f"The total mass of helium need to fill the COPV is {totalMass_COPV.to_base_units():.4f}")

mass_He_fill = density_HE_fill * fillTank_vol  # intital mass of the helium inside the fill tank 
print(f"The mass of helium in the fill tank is {mass_He_fill.to_base_units():.4f}")

equal_den = mass_He_fill / (COPV_vol + fillTank_vol)    # finds the density of helium when the tanks are at equilibrium
equal_p = PropsSI('P', 'D', equal_den.magnitude, 'T', temp_system.magnitude, 'helium')    *(ureg.Pa) # uses density at equilibrium to find the equilization pressure
print(f"The equalization pressure of the system is {equal_p.to(ureg.psi):.2f}")  # equalization pressure is around 3980 psi, the leftover 1000 psi is left to the booster to fill


print('\n\n-----Finding the end condtions-----\n')

min_fillTank_d = (mass_He_fill - totalMass_COPV) / fillTank_vol   # the minimum density of heluim inside the fill tank (when the copv is full), will use as a maximum boost pressure needed to generate
min_fillTank_p = PropsSI('P', 'D', min_fillTank_d.magnitude, 'T', temp_system.magnitude, 'helium')   *(ureg.Pa)
print(f"The minimum tank pressure is {min_fillTank_p.to(ureg.psi):.4f}")
mass_He_neededBoost = mass_He_fill - totalMass_COPV
print(f"The mass of helium need to be boosted by the pump is {mass_He_neededBoost.to_base_units():.4f}")


print('\n\n-----Finding run time-----\n')

# must find the rate of volume change first
airDrive_p = airDrive_p.to(ureg.Pa)
std_p = 1    *(ureg.atm)
std_p = std_p.to(ureg.Pa)
std_t = 273.15   *(ureg.K)

# the scfm value of the inputted flow rate
scfm_air = (cfm_air.magnitude / comp_fact) * (airDrive_p.magnitude / std_p.magnitude)  *((ureg.feet)**3 / (ureg.min))
print(f"The scfm into the pump is {scfm_air:.2f}")

# variables for calculations  (everything will be metric)
equal_p = equal_p.to(ureg.Pa)
COPV_p = equal_p.magnitude
gasChamber_vol = gasChamber_vol.to((ureg.m)**3)
fillTank_vol = fillTank_vol.to((ureg.m)**3)

fillTank_p = equal_p.magnitude
chamber_temp = temp_system.magnitude
COPV_temp = chamber_temp
fillTank_temp = chamber_temp
COPV_vol = COPV_vol.to((ureg.m)**3)
time = 0   # time in seconds
comp_time = 0

COPV_mass = equal_den.magnitude * COPV_vol.magnitude
fillTank_mass = equal_den.magnitude * fillTank_vol.magnitude
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

while COPV_mass < totalMass_COPV.to_base_units().magnitude:
    # updating the fill tank values
    start_entropy = PropsSI('S', 'T', fillTank_temp, 'P', fillTank_p, 'helium')
    start_density = fillTank_mass / (fillTank_vol.magnitude + gasChamber_vol.magnitude)
    fillTank_p = PropsSI('P', 'S', start_entropy, 'D', start_density, 'helium')
    fillTank_temp = PropsSI('T', 'S', start_entropy, 'D', start_density, 'helium')
    fillTank_mass -= gasChamber_vol.magnitude * start_density

    # compressing to COPV pressure, known end pressure and mass doesn't change (gas stays in chamber)
    chamber_entropy = PropsSI('S', 'T', fillTank_temp, 'P', fillTank_p, 'helium')   # these values are same as the fill tank
    chamber_mass = start_density * gasChamber_vol.magnitude
    chamber_temp = PropsSI('T', 'S', chamber_entropy, 'P', COPV_p, 'helium')
    new_chamber_den = PropsSI('D', 'T', chamber_temp, 'P', COPV_p, 'helium')
    new_v = chamber_mass / new_chamber_den
    delta_v = gasChamber_vol.magnitude - new_v
    comp_time = delta_v / vol_speed.magnitude
    time += comp_time

    # finding the avergae temperature of the COPV + chamber
    internal_e_chamber = PropsSI('UMASS', 'T', chamber_temp, 'P', COPV_p, 'helium') * chamber_mass
    internal_e_COPV = PropsSI('UMASS', 'T', COPV_temp, 'P', COPV_p, 'helium') * COPV_mass
    total_specific_internal_e = (internal_e_chamber + internal_e_COPV) / (chamber_mass + COPV_mass)
    comp_temp = PropsSI('T', 'U', total_specific_internal_e, 'P', COPV_p, 'helium') # acts as starting temp
    COPV_den = PropsSI('D', 'T', COPV_temp, 'P', COPV_p, 'helium')

    # compressing He into COPV
    upStream_entropy = PropsSI('S', 'T', comp_temp, 'P', COPV_p, 'helium')
    new_density = (new_chamber_den * new_v + COPV_den * COPV_vol.magnitude) / (new_v + COPV_vol.magnitude)
    COPV_temp_new = PropsSI('T', 'S', upStream_entropy, 'D', new_density, 'helium')
    COPV_p_new = PropsSI('P', 'S', upStream_entropy, 'D', new_density, 'helium')
    delta_v = new_v
    comp_time = delta_v / vol_speed.magnitude
    time += comp_time

    # updateing COPV values
    COPV_p = COPV_p_new
    COPV_temp = COPV_temp_new
    density_COPV = PropsSI('D', 'P', COPV_p_new, 'T', COPV_temp_new, 'helium')
    mass_moved_COPV = delta_v * density_COPV
    COPV_mass += mass_moved_COPV


time = time  *(ureg.s)
print(f"\nThe total time to fill the COPV is {time}")
print(f"The mass in the COPV is {COPV_mass:.5f}")
