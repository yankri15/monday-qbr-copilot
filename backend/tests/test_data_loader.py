"""Smoke tests for the customer data layer."""

import unittest
from pathlib import Path

from app.data.loader import DATA_FILE, DATA_RELATIVE_PATH, get_account_by_name, get_all_accounts
from app.models.customer import CustomerAccount


class DataLoaderSmokeTests(unittest.TestCase):
    def test_loads_all_accounts(self) -> None:
        accounts = get_all_accounts()

        self.assertEqual(len(accounts), 5)
        self.assertTrue(all(isinstance(account, CustomerAccount) for account in accounts))

    def test_known_values_match_assignment_examples(self) -> None:
        altura = get_account_by_name("Altura Systems")
        coral = get_account_by_name("Coral Retail")

        self.assertIsNotNone(altura)
        self.assertIsNotNone(coral)
        assert altura is not None
        assert coral is not None

        self.assertEqual(altura.active_users, 420)
        self.assertAlmostEqual(coral.risk_engine_score, 0.73)

    def test_accounts_expose_all_expected_fields(self) -> None:
        account = get_all_accounts()[0]

        self.assertEqual(set(account.model_dump().keys()), set(CustomerAccount.model_fields.keys()))

    def test_dataset_path_is_backend_relative(self) -> None:
        self.assertEqual(
            DATA_RELATIVE_PATH,
            Path("data") / "sample_customers_q3_2025.xlsx",
        )
        self.assertTrue(DATA_FILE.exists())


if __name__ == "__main__":
    unittest.main()
