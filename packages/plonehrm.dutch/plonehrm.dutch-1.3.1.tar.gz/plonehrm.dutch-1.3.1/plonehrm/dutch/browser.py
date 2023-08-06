from Products.plonehrm.browser.substitution import BaseSubstitutionView


class DutchSubstitutionView(BaseSubstitutionView):
    # mapping for substitution localization (English to desired language)
    substitution_translations = {
        '[company_address]': '[werkgever_adres]',
        '[company_city]': '[werkgever_plaats]',
        '[company_legal_name]': '[werkgever_juridische_naam]',
        '[company_postal_code]': '[werkgever_postcode]',
        '[contract_days_per_week]': '[contract_dagen_per_week]',
        '[contract_duration]': '[contract_duur]',
        '[contract_expirydate]': '[contract_einddatum]',
        '[contract_function]': '[contract_functie]',
        '[contract_hours_per_week]': '[contract_uren_per_week]',
        '[contract_part_full_time]': '[contract_part_full_time]',
        '[contract_startdate]': '[contract_startdatum]',
        '[contract_trial_period]': '[contract_proefperiode]',
        '[contract_wage]': '[contract_loon]',
        '[employee_address]': '[medewerker_adres]',
        '[employee_city]': '[medewerker_plaats]',
        '[employee_date_of_birth]': '[medewerker_geboortedatum]',
        '[employee_first_name]': '[medewerker_voornaam]',
        '[employee_full_name]': '[medewerker_volledige_naam]',
        '[employee_initials]': '[medewerker_initialen]',
        '[employee_last_name]': '[medewerker_achternaam]',
        '[employee_official_name]': '[medewerker_officiele_naam]',
        '[employee_place_of_birth]': '[medewerker_geboorteplaats]',
        '[employee_postal_code]': '[medewerker_post_code]',
        '[employee_title]': '[medewerker_aanhef]',
        '[employee_formal_title]': '[medewerker_formele_aanhef]',
        '[previous_contract_startdate]': '[vorig_contract_startdatum]',
        '[today]': '[vandaag]',
        '[today_written_month]': '[vandaag_lang]',
        '[worklocation_address]': '[vestiging_adres]',
        '[worklocation_city]': '[vestiging_plaats]',
        '[worklocation_pay_period]': '[vestiging_loonperiode]',
        '[worklocation_postal_code]': '[vestiging_post_code]',
        '[worklocation_trade_name]': '[vestiging_handelsnaam]',
        '[worklocation_vacation_days]': '[vestiging_vakantiedagen]',
        '[worklocation_contactperson]': '[vestiging_vertegenwoordiger]',
        '[first_contract_startdate]': '[eerste_contract_startdatum]',
    }

    # For migration.  See
    # Products.plonehrm.migration.replace_old_substitution_parameters
    old_parameters = {
        # old: new
        '[werkgever_officiele_naam]': '[werkgever_juridische_naam]',
        }
