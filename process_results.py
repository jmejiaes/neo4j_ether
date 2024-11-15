
import os
import pandas as pd

from plots import plot_bar_chart
from preprocess import save_results_to_csv


def process_results(neo4j_connection, result_dir):
    # lets plot the data with seaborn
    import seaborn as sns

    # Create a custom palette with the Reds color map and reverse it
    palette = sns.color_palette("Reds", n_colors=10)[::-1]

    # similar palette with the Greens color map
    palette2 = sns.color_palette("Greens", n_colors=10)[::-1]

    # palette with the Blues color map
    palette3 = sns.color_palette("Blues", n_colors=10)[::-1]

    # directorio para la consulta 1 dentro del directorio de resultados
    query_1_dir = f"{result_dir}/query_1"

    # Crear directorio para almacenar los resultados
    os.makedirs(query_1_dir, exist_ok=True)

    #  Consulta 1.1
    results = neo4j_connection.get_accounts_most_received_eth()
    query_1_1 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_1_1, "query_1/query_1_1")

    # Graficar los resultados
    plot_bar_chart(query_1_1['account'], query_1_1['total_received'], palette2, 
                    "Top 10 Accounts by Total Received Ether",  "Total Received Ether", "Account","query_1/query_1_1.png")

    #  Consulta 1.2
    results = neo4j_connection.get_accounts_most_sent_eth()
    query_1_2 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_1_2, "query_1/query_1_2")

    # Graficar los resultados
    plot_bar_chart(query_1_2['account'], query_1_2['total_sent'], palette, 
                    "Top 10 Accounts by Total Sent Ether", "Total Sent Ether", "Account", "query_1/query_1_2.png")

    # directorio para la consulta 2 dentro del directorio de resultados
    query_2_dir = f"{result_dir}/query_2"

    # Crear directorio para almacenar los resultados
    os.makedirs(query_2_dir, exist_ok=True)

    #  Consulta 2.1
    results = neo4j_connection.get_most_active_accounts_received_percentage()
    query_2_1 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_2_1, "query_2/query_2_1")

    # Graficar los resultados
    plot_bar_chart(query_2_1['account'], query_2_1['received_percentage'], palette2, 
                    "Top 10 Most Active Accounts by Total Received Transactions", "Account", "Total Received Transactions", "query_2/query_2_1.png")


    #  Consulta 2.2
    results = neo4j_connection.get_most_active_accounts_sent_percentage()
    query_2_2 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_2_2, "query_2/query_2_2")

    # Graficar los resultados
    plot_bar_chart(query_2_2['account'], query_2_2['sent_percentage'], palette, 
                    "Top 10 Most Active Accounts by Total Sent Transactions", "Account", "Total Sent Transactions", "query_2/query_2_2.png")


    # consulta 2.3
    results = neo4j_connection.get_most_active_accounts_total_percentage()
    query_2_3 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_2_3, "query_2/query_2_3")

    # Graficar los resultados
    plot_bar_chart(query_2_3['account'], query_2_3['total_percentage'], palette3, 
                    "Top 10 Most Active Accounts by Total Transactions", "Account", "Total Transactions", "query_2/query_2_3.png")
    
    # directorio para la consulta 4 dentro del directorio de resultados
    query_4_dir = f"{result_dir}/query_4"

    # Crear directorio para almacenar los resultados
    os.makedirs(query_4_dir, exist_ok=True)

    #  Consulta 4.1
    results = neo4j_connection.get_transaction_statistics()
    query_4_1 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_4_1, "query_4/query_4_1")

    #  Consulta 4.2
    results = neo4j_connection.get_internal_transaction_statistics()
    query_4_2 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_4_2, "query_4/query_4_2")

    # directorio para la consulta 5 dentro del directorio de resultados
    query_5_dir = f"{result_dir}/query_5"

    # Crear directorio para almacenar los resultados
    os.makedirs(query_5_dir, exist_ok=True)

    #  Consulta 5.1
    results = neo4j_connection.get_top_account_pairs_external()
    query_5_1 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_5_1, "query_5/query_5_1")

    #  Consulta 5.2
    results = neo4j_connection.get_top_account_pairs_internal()
    query_5_2 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_5_2, "query_5/query_5_2")

    #  Consulta 5.3
    results = neo4j_connection.get_top_pairs_user_to_contract()
    query_5_3 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_5_3, "query_5/query_5_3")

    #  Consulta 5.4
    results = neo4j_connection.get_top_pairs_contract_to_user()
    query_5_4 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_5_4, "query_5/query_5_4")

    #  Consulta 5.5
    results = neo4j_connection.get_top_pairs_user_to_user()
    query_5_5 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_5_5, "query_5/query_5_5")

    # directorio para la consulta 6 dentro del directorio de resultados
    query_6_dir = f"{result_dir}/query_6"

    # Crear directorio para almacenar los resultados
    os.makedirs(query_6_dir, exist_ok=True)

    #  Consulta 6
    results = neo4j_connection.get_top_account_pairs_by_value_sent()
    query_6 = pd.DataFrame(results, columns=results.keys())

    # Guardar los resultados en un archivo CSV
    save_results_to_csv(query_6, "query_6/query_6")

    return


def common_results():
    # crear direcorio 'comunes'
    comunes_dir = f"comunes"

    # Crear directorio para almacenar los resultados
    os.makedirs(comunes_dir, exist_ok=True)

    directorios_querys = ['results_for_2_(20512878_20512879)','results_for_11_(20512878_20512888)', 'results_for_50_(20512889_20512938)']
    querys = ['query_1_1', 'query_1_2', 'query_2_1', 'query_2_2', 'query_2_3', 'query_4_1', 'query_4_2', 'query_5_1', 'query_5_2', 'query_5_3', 'query_5_4', 'query_5_5', 'query_6']

    # Se itera por cada una de las querys
    for query in querys[:5]:
        # se crea una lista de dataframes
        dataframes = []
        for directorio in directorios_querys:
            # se leen los archivos de cada directorio
            df = pd.read_csv(f"{directorio}/{query[:-2]}/{query}.csv")
            dataframes.append(df)

        # Se hace un merge de los dataframes para obervar cuales aparecen en todos los dataframes
        common = dataframes[0]
        for df in dataframes[1:]:
            common = pd.merge(common, df, how='inner', on='account')
        print(query)

        # Save the resuls to a CSV file with pandas to_csv
        common.to_csv(f"{comunes_dir}/{query}.csv", index=False)

    return