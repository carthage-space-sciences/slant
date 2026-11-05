"""SLANT power and mass estimate (31 October 2026).

Power is a datasheet estimate; mass comes from the CAD model. No figure here is a measurement at the
operating point (0.5 frame/s, five row windows).

Sources
  CM5   Raspberry Pi CM5 datasheet, release 3, Table 9, typical at 5 V:
        idle 400 mA, operating 900 mA, shutdown with PMIC_EN low 1.3 mA, PMIC_EN high 3 mA.
  Head  XIMEA xiJ technical manual v260126, Table 3, at 20 V: idle 2.5 W (powered, not initialized),
        typical 3.4 W (streaming at the most power-intensive mode, no cooling). The detector is uncooled.
  Carrier transceivers and housekeeping: 0.30 W acquiring, 0.10 W idle (allocation).
  Converter efficiency 0.85. Duty: 80 min of acquisition a day in 10 passes; 60 s CM5 boot per pass.
  Pass power: the host switches SLANT on a minute before each sunset, at a time SLANT reports, and off
  after the pass (concept 3 below). Concepts 1 and 2 keep the unit powered between passes, for comparison.
  Mass: housing assembly CAD model 714 g; the board arrangement used removes 53.1 g and its parts add
  3.6 g, with about 1.0 g of passives not drawn.
"""
EFF, DUTY, PASSES, BOOT_S = 0.85, 80 / 1440, 10, 60.0
CM5_IDLE, CM5_OP, CM5_OFF = 0.400 * 5, 0.900 * 5, 0.003 * 5
HEAD_IDLE, HEAD_TYP = 2.5, 3.4
COOLER = 0.0
CAR_ACQ, CAR_IDLE = 0.30, 0.10
boot = PASSES * BOOT_S / 86400

print("ACQUIRING, at the host bus (W)")
acq = {}
for name, cm5, head in (("low: CM5 idle figure, head idle figure", CM5_IDLE, HEAD_IDLE),
                        ("high: CM5 operating, head streaming typical", CM5_OP, HEAD_TYP)):
    loads = cm5 + head + COOLER + CAR_ACQ
    acq[name] = loads / EFF
    print(f"  {name:46s} loads {loads:5.2f} W (5 V converter rated 10 W)  bus {loads/EFF:5.2f} W")

print("\nBETWEEN PASSES and ORBIT AVERAGE (W)")
for concept, idle_loads, extra in (
        ("1 CM5 stays on at idle; head off", CM5_IDLE + CAR_IDLE, 0.0),
        ("2 CM5 shut down (PMIC_EN high), booted 60 s before each pass", CM5_OFF + CAR_IDLE, boot * (CM5_IDLE + CAR_IDLE) / EFF)):
    idle = idle_loads / EFF
    t_idle = 1 - DUTY - (boot if extra else 0)
    for name, a in acq.items():
        print(f"  concept {concept}: idle {idle:4.2f} W; {name.split(':')[0]}: orbit average {DUTY*a + t_idle*idle + extra:4.2f} W")
for name, a in acq.items():
    # concept 3: power off between passes; each pass adds a 60 s boot at CM5 idle and carrier idle
    print(f"  concept 3 host switches power off between passes: idle 0.00 W; {name.split(':')[0]}: "
          f"orbit average {DUTY*a + boot*(CM5_IDLE + CAR_IDLE)/EFF:4.2f} W")

m = 714 - 53.1 + 0.67 + 2.93 + 1.0
print(f"\nMASS, modeled: about {m:.0f} g (CAD model, nominal densities)")
