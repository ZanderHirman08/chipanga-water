# What else to ask Charlie for

Your read is mostly right — the QField package + climate averages + nameplate pump rate gets us a defensible model. But there are a handful of things that would meaningfully sharpen the donor narrative and the calc model, most of which Charlie can knock out in an hour at the site.

I've split them into "really worth asking" and "nice to have."

## Really worth asking (tier 1 — high impact, low effort)

These change either the headline numbers in the dashboard or the credibility of the donor story:

### 1. Actual measured pump flow rate
The model uses the **5,000 L/hr nameplate**. The real number depends on pipe friction, head pressure, and pump wear. Once the pump is running, ask Charlie to:
- Run the pump for 5 minutes
- Time how long it takes to fill a 20 L bucket from a tap downstream of the tank (or measure tank rise)
- Send the number
This is the single number that everything cascades from. If it's actually 4,200 L/hr instead of 5,000, the model should reflect it.

### 2. Static water level + drawdown
Once the pump runs for ~1 hour straight at peak flow, ask him to measure:
- Water level when the pump is OFF (static level)
- Water level when the pump has been running for an hour (dynamic level)
The difference is **drawdown** — tells us whether 5,000 L/hr is actually sustainable or whether the well will run dry under the modeled load. Cheap insurance against an embarrassing donor surprise later.

### 3. Beneficiary counts (real, not derived)
The dashboard says "~400 people fed" — derived from food output ÷ FAO serving size. Donors will want the **actual reach**:
- School enrollment (number of students)
- Number of teachers/staff
- Number of women in the women's-garden cooperative
- Estimated household sizes for the women (so we know roughly how many family members benefit)
Often more compelling: "1 well serves a 400-student school + 10 women's families ≈ 450 direct beneficiaries" lands harder than the derived calculation.

### 4. Photos
The QField schemas have `photo_path` on every layer, so as Charlie collects features he can attach photos in-app. Beyond that, ask for a few setting photos:
- The well being drilled (process shots)
- Existing school buildings (one wide shot, one of a classroom interior)
- Where the gardens will go (current state — bare land vs anything planted)
- The wider landscape (so donors get a sense of place)
- The women's cooperative meeting (with permission) — humanizes the project enormously
If/when the dashboard goes live on GitHub Pages, photos can be added as a gallery section.

### 5. Solar panel wattage per panel + total array kW
The model has `panel_count = 12` and `panel_watts` as a placeholder field on the `solar_array` layer in QField. When Charlie installs/observes them, ask him to fill in:
- Per-panel wattage (e.g., 400W per panel)
- Total system wattage
This confirms the 12-panel array can actually drive a 5,000 L/hr pump through Dodoma's high solar season. Mismatched solar-to-pump sizing is a common third-world project failure mode.

## Nice to have (tier 2 — sharpens the model)

These would refine the calc model assumptions but aren't blockers:

### 6. Soil type at the garden site
Clay vs sandy loam vs loam dramatically changes evapotranspiration and irrigation efficiency. Charlie can either:
- Ask the local agricultural extension office (Bahi District has one)
- Do a simple field test: roll moist soil into a ribbon — long ribbon = clay, falls apart = sand, holds shape briefly = loam.
This lets us swap the generic FAO defaults for soil-specific values.

### 7. Existing rainwater catchment from school roof
Look at the school buildings — corrugated metal roofs in Tanzania are common and a 100 m² roof captures ~58 m³ per year in Dodoma's rainfall. If any rainwater capture exists (or could be added cheaply), it materially changes the wet-season story.
- How big are the school roofs (rough m²)?
- Any existing gutters / tanks for the roof?

### 8. Local crop varieties used
The model uses generic FAO crop coefficients for "leafy greens" and "tomato." If Charlie can name the specific varieties the women grow (e.g., **Sukuma wiki** vs **amaranthus** for greens; specific tomato cultivars), the yield + water assumptions get more accurate. Ask him to chat with the cooperative.

### 9. Market context
For donor reporting, food output in **kg/year** is fine, but **TZS/year** (or USD/year) hits harder.
- Distance to the nearest market town
- Rough TZS/kg price for tomato, leafy greens, okra at local market in dry season
- Are women already selling produce, or is this for household consumption?

## Lower priority (tier 3 — future-proofing)

These aren't urgent but are worth knowing:

- **Cellular signal at the site** — even though we're not building real-time sensors, if there's good signal, future iterations could add a flow meter with a cellular logger.
- **Spare-parts plan** — pump impeller, filter, solar panel replacements. Where does Charlie source these? What's the failure mode plan for year 2 once Charlie is gone?
- **Local maintenance contact** — name + phone of a fundi (handyman) who can service the pump/solar. Sustainability depends on this far more than on the original install quality.

## What I'd send Charlie tonight (one WhatsApp message)

> "Quick asks for the project doc — when you can, send:
>
> 1. Actual pump flow rate (5 min bucket test once it's running)
> 2. Static water level + level after pumping ~1 hr
> 3. School enrollment, # teachers, # women in garden coop
> 4. A few setting photos (well, school, garden site, the cooperative if they're cool with it)
> 5. Per-panel solar wattage
>
> No rush — these refine the dashboard and the donor story. If you're already filling out the QField stuff that covers most of it; these are the gaps."

The QField package you sent already covers the spatial side. These five are the non-spatial gaps.
