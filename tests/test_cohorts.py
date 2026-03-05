import unittest

from open_launch_analytics.cohorts import build_signup_cohorts


class SignupCohortTests(unittest.TestCase):
    def test_build_signup_cohorts_computes_d0_d1_d7_rates(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "signup",
                "timestamp": "2026-03-01T09:00:00Z",
                "user_id": "u1",
                "utm_source": "LinkedIn",
                "utm_campaign": "Spring",
            },
            {
                "event_id": "evt_2",
                "event_name": "activation",
                "timestamp": "2026-03-01T12:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_3",
                "event_name": "activated",
                "timestamp": "2026-03-02T08:30:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_4",
                "event_name": "signup",
                "timestamp": "2026-03-01T10:00:00Z",
                "user_id": "u2",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_5",
                "event_name": "activation",
                "timestamp": "2026-03-08T08:00:00Z",
                "user_id": "u2",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
        ]

        rows = build_signup_cohorts(events)

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["cohort_date"], "2026-03-01")
        self.assertEqual(row["signups"], 2)

        self.assertEqual(row["d0_activated"], 1)
        self.assertEqual(row["d1_activated"], 1)
        self.assertEqual(row["d7_activated"], 1)

        self.assertEqual(row["d0_rate"], 0.5)
        self.assertEqual(row["d1_rate"], 0.5)
        self.assertEqual(row["d7_rate"], 0.5)

    def test_build_signup_cohorts_supports_source_campaign_filters(self):
        events = [
            {
                "event_id": "evt_1",
                "event_name": "signup",
                "timestamp": "2026-03-03T09:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_2",
                "event_name": "activation",
                "timestamp": "2026-03-03T11:00:00Z",
                "user_id": "u1",
                "utm_source": "linkedin",
                "utm_campaign": "spring",
            },
            {
                "event_id": "evt_3",
                "event_name": "signup",
                "timestamp": "2026-03-03T09:00:00Z",
                "user_id": "u2",
                "utm_source": "reddit",
                "utm_campaign": "launch",
            },
            {
                "event_id": "evt_4",
                "event_name": "activation",
                "timestamp": "2026-03-03T12:00:00Z",
                "user_id": "u2",
                "utm_source": "reddit",
                "utm_campaign": "launch",
            },
        ]

        rows = build_signup_cohorts(
            events,
            utm_source=" linkedin ",
            utm_campaign="SPRING",
        )

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["signups"], 1)
        self.assertEqual(row["d0_activated"], 1)
        self.assertEqual(row["d0_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
