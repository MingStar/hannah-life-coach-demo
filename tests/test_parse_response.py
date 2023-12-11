from app.daily_journal.todo_parser import get_jsons


def test_parse_response():
    response = """
start
{["summary"]}
middle
{"todo": "blah #label"}
end"""
    text, jsons = get_jsons(response)
    assert len(jsons) == 2
    assert jsons[0] == '{["summary"]}'
    assert jsons[1] == '{"todo": "blah #label"}'
    assert (
        text
        == """
start

middle

end"""
    )
