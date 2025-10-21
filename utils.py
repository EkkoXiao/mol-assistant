import json
import requests
import streamlit as st
import networkx as nx
import plotly.graph_objects as go

API_URL = "https://4020f1c8d6e1.ngrok-free.app"
# API_URL = "http://localhost:8000"
API_URL2 = "https://cesar-unfulminating-patricia.ngrok-free.dev"


@st.cache_resource
def load_html(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def get_score_color(score: float) -> str:
    score = max(0, min(150, score))

    color_stops = [
        (0, 0xF4, 0x43, 0x36),
        (37.5, 0xFF, 0x69, 0x34),
        (75, 0xFF, 0xC1, 0x07),
        (112.5, 0xCD, 0xDC, 0x39),
        (150, 0x4C, 0xAF, 0x50),
    ]

    for i in range(len(color_stops) - 1):
        start_pos, r1, g1, b1 = color_stops[i]
        end_pos, r2, g2, b2 = color_stops[i + 1]

        if start_pos <= score <= end_pos:
            ratio = (score - start_pos) / (end_pos - start_pos)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            return f"#{r:02X}{g:02X}{b:02X}"

    return "#F44336"


def get_network_data(cell_line: str, drugs: list[str]) -> dict | None:
    try:
        resp = requests.post(
            f"{API_URL2}/dsp",
            json={"cell_line": cell_line, "drugs": drugs},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"获取网络图数据失败: {str(e)}")
        return None


def display_network_graph(network_data: dict) -> None:
    if not network_data or "nodes" not in network_data or "edges" not in network_data:
        st.write(network_data)
        st.warning("网络图数据错误")
        return

    nodes = network_data["nodes"]
    edges = network_data["edges"]
    st.subheader("🔗 Interaction Network")

    try:
        G = nx.Graph()

        node_info: dict[str, dict[str, str]] = {}
        for node in nodes:
            node_type = node.split(": ")[0] if ": " in node else "unknown"
            node_name = node.split(": ")[1] if ": " in node else node
            G.add_node(node, type=node_type, name=node_name)
            node_info[node] = {"type": node_type, "name": node_name}

        for edge in edges:
            src = edge.get("src", "")
            dst = edge.get("dst", "")
            attribute = edge.get("attribute", "")
            if src and dst and src in G.nodes and dst in G.nodes:
                G.add_edge(src, dst, attribute=attribute)

        pos = nx.spring_layout(G, k=3, iterations=50)

        node_x: list[float] = []
        node_y: list[float] = []
        node_colors: list[str] = []
        node_sizes: list[int] = []
        node_label_texts: list[str] = []
        node_hover_texts: list[str] = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            node_type = node_info[node]["type"]
            node_name = node_info[node]["name"]

            if node_type == "drug":
                color = "#4CAF50"
                size = 30
                icon = "💊"
            elif node_type == "protein":
                color = "#2196F3"
                size = 15
                icon = "🧬"
            elif node_type == "cellline":
                color = "#FF9800"
                size = 24
                icon = "🎯"
            else:
                color = "#9E9E9E"
                size = 12
                icon = "⚪"

            node_colors.append(color)
            node_sizes.append(size)
            node_label_texts.append(f"{icon} {node_name}")
            node_hover_texts.append(f"{icon} {node_name}<br>类型: {node_type}")

        edge_x: list[float] = []
        edge_y: list[float] = []
        edge_info: list[str] = []
        edge_text_lines: list[str] = []
        edge_label_x: list[float] = []
        edge_label_y: list[float] = []
        edge_labels: list[str] = []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            edge_attr = G[edge[0]][edge[1]].get("attribute", "")
            attr_display = edge_attr
            try:
                attr_str = str(edge_attr).strip()
                parts = attr_str.split()
                if len(parts) >= 2 and parts[0].lower() == "expression":
                    value = float(parts[1])
                    attr_display = f"expression {value:.3f}"
            except Exception:
                attr_display = edge_attr

            edge_info.append(f"{edge[0]} → {edge[1]}<br>关系: {attr_display}")
            edge_text_lines.append(f"- {edge[0]} → {edge[1]}: {edge_attr}")
            edge_label_x.append((x0 + x1) / 2)
            edge_label_y.append((y0 + y1) / 2)
            edge_labels.append(attr_display)

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=2, color="#888"),
                hoverinfo="none",
                mode="lines",
                name="连接",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=edge_label_x,
                y=edge_label_y,
                mode="text",
                text=edge_labels,
                textposition="middle center",
                textfont=dict(size=12, color="black"),
                hoverinfo="skip",
                name="关系",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                hoverinfo="text",
                hovertext=node_hover_texts,
                text=node_label_texts,
                textposition="middle right",
                textfont=dict(size=14, color="black"),
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=2, color="white"),
                    opacity=0.8,
                ),
                name="节点",
            )
        )

        fig.update_layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="💊 药物 | 🧬 蛋白质 | 🎯 细胞系",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.005,
                    y=-0.002,
                    xanchor="left",
                    yanchor="bottom",
                    font=dict(color="gray", size=12),
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="white",
            height=600,
        )

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"网络图生成失败: {str(e)}")

