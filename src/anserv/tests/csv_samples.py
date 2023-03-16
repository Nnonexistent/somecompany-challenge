from typing import Any, Dict, List, Tuple

VALID_SAMPLES: List[Tuple[str, Dict[str, Any]]] = [
    (  # basic
        """
review_time,team,date,merge_time
0,Application,2023-01-14,0
144299,Application,2023-02-14,1076
0,Data Service,2023-01-14,0
77,Platform,2023-02-14,102
        """.strip(),
        {
            'date_start': '2023-01-14',
            'date_end': '2023-02-14',
            'teams': ['Application', 'Data Service', 'Platform'],
            'merge_time_min': 0,
            'merge_time_mean': 294.5,
            'review_time_max': 144299,
            'review_time_median': 38.5,
        },
    ),
    (  # Zeros and empty strings
        """
review_time,team,date,merge_time
0,,2023-01-01,0
0,,2023-01-02,0
        """.strip(),
        {
            'date_start': '2023-01-01',
            'date_end': '2023-01-02',
            'teams': [''],
            'merge_time_min': 0,
            'merge_time_mean': 0,
            'review_time_max': 0,
            'review_time_median': 0,
        },
    ),
    (  # Wrong order, extra cols
        """
team,date,merge_time,review_time,extra
Qwe,2023-01-01,100,100,zxc
Asd,2023-01-02,100,100,zxc
        """.strip(),
        {
            'date_start': '2023-01-01',
            'date_end': '2023-01-02',
            'teams': ['Qwe', 'Asd'],
            'merge_time_min': 100,
            'merge_time_mean': 100,
            'review_time_max': 100,
            'review_time_median': 100,
        },
    ),
]

INVALID_SAMPLES: List[str] = [
    # Duplicates
    """
review_time,team,date,merge_time
0,Qwe,2023-01-01,0
0,Qwe,2023-01-01,0
    """.strip(),
    # Empty
    '',
    # Empty, but valid header
    """
review_time,team,date,merge_time
    """.strip(),
    # Not enough headers
    """
review_time,team,date
0,Qwe,2023-01-01
    """.strip(),
    # Invalid format
    """
review_time,team,date,merge_time
0,Qwe,202301,0
    """.strip(),
    # Not enough values
    """
review_time,team,date,merge_time
0,Qwe,2023-01-01,0
0,Qwe,2023-01-01
    """.strip(),
]
