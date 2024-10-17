import matplotlib.pyplot as plt

def plot_bar_chart(x, y, palette, title, x_label, y_label, filename, cantidad_bloques):

    # trunca las direcciones de las cuentas para una mejor visualizacion
    x = x.str[:6] + '...' + x.str[-6:]
    

    plt.figure(figsize=(14, 8))

    # Crear el gráfico de barras horizontales
    plt.barh(x, y, color=palette)

    # Etiquetas de los ejes
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(f'{title} ({cantidad_bloques} blocks)')

    # Mostrar el valor de las barras al final de cada barra horizontal
    for i, v in enumerate(y):
        plt.text(v + 0.1, i, str(round(v, 2)), va='center')

    # Eliminar bordes del gráfico
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)

    # Asegurar que el gráfico no corte ningún elemento
    plt.tight_layout()

    # Guardar la gráfica con bbox_inches="tight"
    plt.savefig(f"{result_dir}/{filename}", bbox_inches="tight")

    plt.show()  # Mostrar la gráfica