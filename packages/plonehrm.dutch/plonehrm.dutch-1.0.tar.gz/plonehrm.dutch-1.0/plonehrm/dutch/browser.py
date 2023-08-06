from Products.plonehrm.browser.substitution import BaseSubstitutionView


class DutchSubstitutionView(BaseSubstitutionView):
    # mapping for substitution localization (English to desired language)
    substitution_translations = {
        '[company_address]': '[werkgever_adres]',
        '[company_postal_code]': '[werkgever_postcode]',
        '[company_city]': '[werkgever_plaats]',
        '[company_official_name]': '[werkgever_officiele_naam]',
        '[contract_duration]': '[contract_duur]',
        '[contract_expirydate]': '[contract_einddatum]',
        '[contract_function]': '[contract_functie]',
        '[contract_hours_per_week]': '[contract_uren_per_week]',
        '[contract_days_per_week]': '[contract_dagen_per_week]',
        '[contract_part_full_time]': '[contract_part_full_time]',
        '[contract_startdate]': '[contract_startdatum]',
        '[contract_trial_period]': '[contract_proefperiode]',
        '[contract_wage]': '[contract_loon]',
        '[employee_address]': '[medewerker_adres]',
        '[employee_city]': '[medewerker_plaats]',
        '[employee_date_of_birth]': '[medewerker_geboortedatum]',
        '[employee_title]': '[medewerker_aanhef]',
        '[employee_initials]': '[medewerker_initialen]',
        '[employee_last_name]': '[medewerker_achternaam]',
        '[employee_official_name]': '[medewerker_officiele_naam]',
        '[employee_place_of_birth]': '[medewerker_geboorteplaats]',
        '[employee_postal_code]': '[medewerker_post_code]',
        '[previous_contract_startdate]': '[vorig_contract_startdatum]',
        '[today]': '[vandaag]',
        '[worklocation_address]': '[vestiging_adres]',
        '[worklocation_postal_code]': '[vestiging_post_code]',
        '[worklocation_city]': '[vestiging_plaats]',
        '[worklocation_trade_name]': '[vestiging_handelsnaam]',
        '[worklocation_vacation_days]': '[vestiging_vakantiedagen]',
    }
