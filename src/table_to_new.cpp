#include <vector>
#include <string>
#include <sstream>
#include <memory>
#include <cstring>
#include <cstdlib>
using namespace std;

vector<vector<string>> table_to_new(string table)
{
    vector<vector<string>> table_list;
    if (table.empty() || table.find('|') == string::npos)
    {
        return table_list;
    }
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
    vector<vector<string>> table_to_new_wrapper(const string &table)
    {
        vector<vector<string>> table_list = table_to_new(table);
        int rows = table_list.size();
        int cols = table_list[0].size();
        vector<vector<string>> result(rows, vector<string>(cols));
        for (int i = 0; i < rows; i++)
        {
            for (int j = 0; j < cols; j++)
            {
                std::ostringstream oss;
                oss << table_list[i][j];
                result[i][j] = oss.str();
            }
        }
        return result;
    }
}
