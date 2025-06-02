import streamlit as st
import streamlit_shadcn_ui as ui # Assuming this is the import convention

data = {
    "drug1": "Alpelisib",
    "drug2": "Copanlisib",
    "score": 0.305,
    "explanation": "Alpelisib和Copanlisib通过与各自的作用靶点结合，协同对抗癌症，共同抑制癌细胞的生长和分裂。 Alpelisib作用于磷脂酰肌醇4,5-二磷酸3-核糖合酶家族成员1（PAI-3），而 Copanlisib则作用于磷脂酰肌醇4,5-二磷酸3-核糖合酶家族成员1。它们通过协同作用，共同发挥抗癌作用。"
}

# This is a conceptual example as the exact API for streamlit-shadcn-ui's card
# might vary. Please refer to its documentation.
# It's likely you'd build the card content using other shadcn components or markdown.

with ui.card(title=f"Combination: {data['drug1']} & {data['drug2']}",
             description=f"Synergy Score: {data['score']}",): # Example class for styling
    ui.label(text="Explanation:")
    ui.paragraph(text=data['explanation'])

# OR, if it allows more direct content:
# ui.card(
#     title=f"Drug Combination: {data['drug1']} & {data['drug2']}",
#     content=f"""
#         **Score:** {data['score']}<br><br>
#         **Explanation:**<br>
#         {data['explanation']}
#     """,
#     class_name="p-4" # Example padding
# )

st.markdown("---") # Separator

# More detailed construction using shadcn components within a card
# (Conceptual - check the library's specific API)
with ui.card(class_name="w-full max-w-lg mx-auto mt-4"):
    with ui.card_header():
        ui.card_title(text=f"{data['drug1']} + {data['drug2']}")
        ui.card_description(text=f"Synergy Score: {data['score']:.3f}")
    with ui.card_content():
        st.markdown(f"**Explanation:**\n\n{data['explanation']}")
    with ui.card_footer():
        ui.button(text="More Info", variant="outline", class_name="mr-2")
        ui.button(text="Save")