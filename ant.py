# Алгоритмы
from random import randint, choices, random
import networkx as nx
import ant_common

# Импорт параметров
h_rel, p_rel, ant_n, p_count, ev_rate, iters, gamma, q0= ant_common.args.values()

# Класс муравья
class Ant:
    # Конструктор класса
    def __init__(self, graph: nx.Graph):
        self.g = graph
        self.pos = randint(1, len(self.g.nodes))
        self.visited_edges = []
        self.visited_vertices = []
        self.visited_vertices.append(self.pos)
        self.path_len = 0

    # Поиск следующего ребра
    def next(self):
        # Ребра инцидентные текущей вершине к непосещенным вершинам
        edges = [edge for edge in self.g.edges(self.pos, data=True) if edge[1] not in self.visited_vertices]
        # Возврат если таких ребер нет
        if len(edges) == 0:
            return False
        # Вычисление весов для всех ребер
        weights = [edge[2]['pheromone'] ** p_rel * (1 / edge[2]['weight']) ** h_rel for edge in edges]
        # С вероятностью 1-q0 выбираем лучшее ребро
        if random() < q0:
            chosen = edges[weights.index(max(weights))]
        # Иначе выбираем случайно-пропорционально
        else:
            chosen = choices(edges, weights=weights, k=1)[0]
        # Обновляем параметры в соответствии с выбранным ребром
        self.pos = chosen[1]
        self.visited_edges.append(chosen)
        self.visited_vertices.append(self.pos)
        self.path_len += chosen[2]['weight']
        return True

    # Построение цикла
    def route(self):
        v_count = len(self.g.nodes)
        # Строим цикл (если получилось)
        while len(self.visited_vertices) != v_count:
            if not self.next():
                return -1
        # Добавляем замыкающее ребро
        if v_count != 1:
            last = self.pos
            start = self.visited_edges[0][0]
            if self.g.has_edge(last, start) and v_count != 2:
                length = self.g.edges[last, start]['weight']
                pheromone = self.g.edges[last, start]['pheromone']
                self.visited_edges.append((last, start, {'weight': length, 'pheromone': pheromone}))
                # Обновляем феромон
                self.update()
            else:
                return -1
        # Возвращаем длину пути и путь (если цикл построен)
        return self.path_len, self.visited_edges

    # 1 этап обновления феромона
    def update(self):
        for i in range(len(self.visited_edges) - 1):
            curr = self.visited_edges[i]
            if i == len(self.visited_edges) - 2:
                curr[2]['pheromone'] = (1 - ev_rate) * curr[2]['pheromone'] + \
                                       ev_rate * gamma * self.visited_edges[-1][2]['pheromone']
            else:
                curr[2]['pheromone'] = (1 - ev_rate) * curr[2]['pheromone'] +\
                                   ev_rate * gamma * max([edge[2]['pheromone'] for edge in
                                                          self.g.edges(curr[1], data=True)
                                                          if edge[1] not in self.visited_vertices[0:1+i]])


# 2 этап обновления феромона
def update_pheromone(graph: nx.Graph, iter_best: tuple):
    path_len, path = iter_best
    for edge in path:
        edge[2]['pheromone'] = (1 - ev_rate) * edge[2]['pheromone'] + p_count / path_len
        graph.edges[edge[0], edge[1]]['pheromone'] += p_count / path_len

# Собственно алгоритм
def aco(graph: nx.Graph) -> [nx.Graph, float]:
    # Обновляем параметры
    global h_rel, p_rel, ant_n, p_count, ev_rate, iters, gamma, q0
    h_rel, p_rel, ant_n, p_count, ev_rate, iters, gamma, q0= ant_common.args.values()

    # Список найденных путей и лучший путь
    results = []
    iter_best = None

    # Присваиваем начальное значение феромона
    for edge in graph.edges(data=True):
        edge[2]['pheromone'] = 1
    for i in range(iters):
        # Строим колонию
        colony = [Ant(graph) for _ in range(ant_n)]
        # Заполняем пути, выбираем только те, которые построились полностью
        results = list(filter(lambda x: x != -1, [ant.route() for ant in colony]))
        # Если есть хотя бы 1 путь
        if results:
            # Ищем лучший путь
            iter_best = min(results, key=lambda x: x[0])
            # Обновляем феромон
            update_pheromone(graph, iter_best)
            print(f'Iter: {i}, sol: {iter_best[0]}')
        # Иначе сообщаем об отсутствии решения
        else:
            ant_common.info('No solution found')
            break
    if results:
        path_len, path = iter_best
        if path_len:
            # Строим выходной орграф и возвращаем его
            out = nx.DiGraph()
            out.add_edges_from(path)
            return out, path_len
    # Возвращаем пустой граф если решения нет
    return nx.DiGraph(), 0
