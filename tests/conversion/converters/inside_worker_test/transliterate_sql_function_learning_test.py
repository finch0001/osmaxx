from contextlib import closing

import pytest
import sqlalchemy

from tests.conversion.converters.inside_worker_test.conftest import slow

international_text_strings = [
    ('ascii', 'some normal ascii', 'some normal ascii'),
    ('umlaut', 'öäüüäüö', 'öäüüäüö'),
    ('special_chars', "*+?'^'%ç#", "*+?'^'%ç#"),
    ('japanese', "大洲南部広域農道", 'dà zhōu nán bù guǎng yù nóng dào'),
    ('chinese russian', "二连浩特市 Эрээн хот", 'èr lián hào tè shì Éréén hot'),
    ('arabic', "شارع المنيرة الرئيسي", 'sẖạrʿ ạlmnyrẗ ạlrỷysy'),
    # transliteration doesn't work on eritrean characters!
    ('eritrean', 'ጋሽ-ባርካ', 'ጋሽ-ባርካ'),
]


@pytest.fixture(params=international_text_strings)
def international_text(request):
    return dict(
        variant=request.param[0],
        text=request.param[1],
        expected=request.param[2],
    )


@slow
def test_osml10n_translit_works_as_expected(osmaxx_functions, international_text):
    engine = osmaxx_functions
    text_escaped = international_text['text']
    with closing(engine.execute(sqlalchemy.text("select osml10n_translit($${}$$) as label;".format(text_escaped)).execution_options(autocommit=True))) as result:
        assert result.rowcount == 1
        results = result.fetchall()
        assert len(results) == 1
        assert results[0]['label'] == international_text['expected']
