from typing import Any, Callable, Dict, Type

import pytest
from fastapi.testclient import TestClient

from db.orm import EntryOrm, VisualizationOrm
from vis.vis_types import AnyVisType, DateByTypeVis, ReviewMergeRatioVis, ReviewOverMergeVis

CSV_DATA = """
team,date,merge_time,review_time
Qwe,2023-01-01,10,10
Qwe,2023-01-02,10,10
Asd,2023-01-01,100,100
Asd,2023-01-02,100,100
"""


@pytest.mark.parametrize(
    'vis_type_class,vis_type_kwargs,expected_len,expected_item',
    [
        (
            DateByTypeVis,
            {'date_resolution': 'day'},
            8,
            {'date': '2023-01-01', 'value': 10, 'type': 'review', 'team': 'Qwe'},
        ),
        (  # aggregates by weeks
            DateByTypeVis,
            {'date_resolution': 'week'},
            4,
            {'date': '2023-01-02', 'value': 20, 'type': 'review', 'team': 'Qwe'},
        ),
        (  # filter one team
            DateByTypeVis,
            {'date_resolution': 'day', 'filters': [{'filter_type': 'teams', 'teams': ['Asd']}]},
            4,
            {'date': '2023-01-01', 'value': 100, 'type': 'review', 'team': 'Asd'},
        ),
        (  # filter half of dates
            DateByTypeVis,
            {'date_resolution': 'day', 'filters': [{'filter_type': 'date-range', 'start_date': '2023-01-02'}]},
            4,
            {'date': '2023-01-02', 'value': 10, 'type': 'review', 'team': 'Qwe'},
        ),
        (  # apply both filters
            DateByTypeVis,
            {
                'date_resolution': 'day',
                'filters': [
                    {'filter_type': 'teams', 'teams': ['Asd']},
                    {'filter_type': 'date-range', 'start_date': '2023-01-02'},
                ],
            },
            2,
            {'date': '2023-01-02', 'value': 100, 'type': 'review', 'team': 'Asd'},
        ),
        (
            ReviewOverMergeVis,
            {},
            4,
            {'merge_value': 10, 'review_value': 10, 'date': '2023-01-02', 'team': 'Qwe'},
        ),
        (
            ReviewMergeRatioVis,
            {},
            4,
            {'value': 20, 'type': 'review', 'team': 'Qwe'},
        ),
    ],
)
def test_date_by_type_vis(
    api_client: TestClient,
    entry_factory: Callable[..., EntryOrm],
    vis_factory: Callable[..., VisualizationOrm],
    vis_type_class: Type[AnyVisType],
    vis_type_kwargs: Dict[str, Any],
    expected_len: int,
    expected_item: Dict[str, Any],
) -> None:
    entry = entry_factory(csv_data=CSV_DATA)
    vis_type = vis_type_class(
        chart_type=vis_type_class.allowed_chart_types[0],
        **vis_type_kwargs,
    )
    vis = vis_factory(entry=entry, vis_type=vis_type, is_public=True)

    with api_client as client:
        response = client.get(f'/vis/{vis.id}/')

    assert response.status_code == 200
    data = response.json()['data']

    assert len(data) == expected_len
    assert expected_item in data
