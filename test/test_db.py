from db_setup import create_table, insert_data

def test_db_operations():
    create_table()
    result = insert_data("Test")
    assert result == "Data inserted successfully"
