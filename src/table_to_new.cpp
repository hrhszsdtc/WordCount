#include <vector>
#include <string>
#include <sstream>
using namespace std;

vector<vector<string>> table_to_new(string table)
{
    vector<vector<string>> table_list;
    stringstream ss(table);
    string table_line;
    while (getline(ss, table_line))
    {
        stringstream ss_line(table_line);
        string token;
        vector<string> line_list;
        while (getline(ss_line, token, '|'))
        {
            if (!token.empty())
            {
                line_list.push_back(token);
            }
        }
        if (!line_list.empty())
        {
            table_list.push_back(line_list);
        }
    }
    table_list.erase(table_list.begin(), table_list.begin() + 2);
    return table_list;
}

extern "C"
{
    char ***table_to_new_wrapper(const char *table)
    {
        string table_str(table);
        vector<vector<string>> table_list = table_to_new(table_str);
        int rows = table_list.size();
        int cols = table_list[0].size();
        char ***result = new char **[rows + 1];
        for (int i = 0; i < rows; i++)
        {
            result[i] = new char *[cols + 1];
            for (int j = 0; j < cols; j++)
            {
                result[i][j] = new char[table_list[i][j].length() + 1];
                strcpy(result[i][j], table_list[i][j].c_str());
            }
            result[i][cols] = nullptr;
        }
        result[rows] = nullptr;
        return result;
    }

    void free_table(char ***table)
    {
        for (int i = 0; table[i] != nullptr; i++)
        {
            for (int j = 0; table[i][j] != nullptr; j++)
            {
                delete[] table[i][j];
            }
            delete[] table[i];
        }
        delete[] table;
    }
}
