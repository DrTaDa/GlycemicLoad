import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Set page title and configuration
st.set_page_config(page_title="Glycemic Index Visualization", layout="wide")
st.title("Glycemic Index and Load Visualization")

# Create sidebar for controls
st.sidebar.header("Controls")

# Add serving size slider to sidebar
serving_size = st.sidebar.slider("Serving Size (grams)", min_value=50, max_value=500, value=100, step=10)

# Food data with categories
ingredients = [
    {"name": "White bread", "gi": 75, "carbs": 49, "category": "Baked goods"},
    {"name": "Whole grain bread", "gi": 58, "carbs": 43, "category": "Baked goods"},
    {"name": "Sourdough bread", "gi": 54, "carbs": 49, "category": "Baked goods"},

    {"name": "Rice (white)", "gi": 73, "carbs": 28, "category": "Grains and pasta"},
    {"name": "Pasta", "gi": 53, "carbs": 25, "category": "Grains and pasta"},
    {"name": "Boiled rolled oats", "gi": 60, "carbs": 60, "category": "Grains and pasta"},

    {"name": "Boiled Potato", "gi": 82, "carbs": 17, "category": "Vegetables"},
    {"name": "Baked Potato", "gi": 111, "carbs": 17, "category": "Vegetables"},
    {"name": "Sweet potato", "gi": 63, "carbs": 20, "category": "Vegetables"},

    {"name": "Apple", "gi": 36, "carbs": 14, "category": "Fruits"},
    {"name": "Banana", "gi": 51, "carbs": 23, "category": "Fruits"},
    {"name": "Orange", "gi": 43, "carbs": 12, "category": "Fruits"},

    {"name": "Kidney beans", "gi": 35, "carbs": 60, "category": "Legumes"},
    {"name": "Lentils", "gi": 32, "carbs": 20, "category": "Legumes"},
    {"name": "Chickpeas", "gi": 28, "carbs": 27, "category": "Legumes"},

    {"name": "Milk chocolate", "gi": 49, "carbs": 59, "category": "Sweets"},
    {"name": "90% dark chocolate", "gi": 23, "carbs": 14, "category": "Sweets"},
    {"name": "Ice cream", "gi": 57, "carbs": 24, "category": "Sweets"},
    {"name": "Honey", "gi": 61, "carbs": 80, "category": "Sweets"},
    {"name": "White sugar", "gi": 64, "carbs": 100, "category": "Sweets"},

    #{"name": "Skimmed milk", "gi": 27, "carbs": 5, "category": "Dairies"},
    {"name": "Plain yogurt", "gi": 27, "carbs": 6, "category": "Dairies"},
]

# Get unique categories
categories = sorted(list(set(item["category"] for item in ingredients)))

# Add category selection to sidebar
selected_categories = st.sidebar.multiselect(
    "Select Food Categories",
    options=categories,
    default=categories
)

# Filter ingredients based on selected categories
filtered_ingredients = [item for item in ingredients if item["category"] in selected_categories]

# Add explanation about Glycemic Index and Load
with st.expander("What are Glycemic Indices ?", expanded=False):
    st.markdown("""
    The **Glycemic Index (GI)** is a measure of how quickly a food raises blood sugar levels compared to pure glucose. 
    - Low GI: 55 or less
    - Medium GI: 56-69
    - High GI: 70 or higher

    Foods with a lower glycemic index are generally better for blood sugar management.
    """)

with st.expander("What is a  Glycemic Load ?", expanded=False):
    st.markdown("""
    **Glycemic Load (GL)** is the product of the GI of the food eaten times the ammount that is eaten:

    GL = (GI × Carbs per serving) ÷ 100

    - Low GL: 10 or less
    - Medium GL: 11-19s
    - High GL: 20 or higher
    
    It is recommended to keep the GL of most meals under 25 and the sum of all GLs for a day under 100.
    """)

with st.expander("Why is there no meat or fish on the graph ?", expanded=False):
    st.markdown("""
    Meat and fish do not contain any sugar, as such they have a GI of 0 and do not increase the blood sugar level.
    """)

# Compute glycemic load and carbs based on serving size
for item in filtered_ingredients:
    item["carbs_per_serving"] = item["carbs"] * serving_size / 100
    item["gl"] = (item["gi"] * item["carbs"] * serving_size) / 10000

# Create DataFrame for the table
if filtered_ingredients:
    df = pd.DataFrame(filtered_ingredients)
    df = df[["name", "gi", "carbs_per_serving", "gl"]]
    df = df.rename(columns={
        "name": "Food",
        "gi": "Glycemic Index",
        "carbs_per_serving": f"Carbs per {serving_size}g (g)",
        "gl": "Glycemic Load"
    })
    df = df.sort_values("Glycemic Load", ascending=True)
    df[f"Carbs per {serving_size}g (g)"] = df[f"Carbs per {serving_size}g (g)"].round(1)
    df["Glycemic Load"] = df["Glycemic Load"].round(1)

    # Create scatter plot
    # Create DataFrame for Plotly
    plot_df = pd.DataFrame({
        "name": [item["name"] for item in filtered_ingredients],
        "category": [item["category"] for item in filtered_ingredients],
        "carbs_per_serving": [round(item["carbs_per_serving"], 1) for item in filtered_ingredients],
        "gi": [item["gi"] for item in filtered_ingredients],
        "gl": [round(item["gl"], 1) for item in filtered_ingredients]
    })

    # Create the Plotly figure
    fig = px.scatter(
        plot_df,
        x="carbs_per_serving",
        y="gi",
        color="gl",
        color_continuous_scale="YlOrRd",
        hover_name="name",
        range_color=[1, 100],
        hover_data={
            "name": False,  # Hide name as it's in the hover title
            "carbs_per_serving": ':.1f',
            "gi": True,
            "gl": ':.1f',
            "category": True
        },
        labels={
            "carbs_per_serving": f"Carbohydrates for {serving_size}g serving (g)",
            "gi": "Glycemic Index",
            "gl": "Glycemic Load",
            "category": "Category"
        },
        size=[48] * len(filtered_ingredients)  # Reduced marker size by 20% (from 60 to 48)
    )

    # Add the GL threshold line
    x_values = np.linspace(0, max(90, plot_df["carbs_per_serving"].max() * 1.2), 1000)
    y_values = 25 * 100 / x_values

    # Filter out infinity values and points outside the range
    valid_indices = np.isfinite(y_values) & (y_values > 0) & (y_values < 200)

    if np.any(valid_indices):

        # Add shaded area for high GL
        y_max = max(1000, plot_df["gi"].max() * 1.2)
        fig.add_trace(
            go.Scatter(
                x=np.concatenate([x_values[valid_indices], [x_values[valid_indices][-1], x_values[valid_indices][0]]]),
                y=np.concatenate([y_values[valid_indices], [y_max, y_max]]),
                fill='toself',
                fillcolor='rgba(255, 0, 0, 0.1)',
                line=dict(color='rgba(255, 0, 0, 0)'),
                hoverinfo='skip',
                showlegend=False
            )
        )

    # Update layout
    fig.update_layout(
        xaxis_title=f"Carbohydrates for {serving_size}g serving (g)",
        yaxis_title="Glycemic Index",
        height=600,
        legend_title="Legend",
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial"
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    # Fix axis ranges to be consistent regardless of selected categories
    fig.update_yaxes(range=[1, 120])
    fig.update_xaxes(range=[0, np.max([90, np.max(plot_df["carbs_per_serving"]) + 10])])

    # Add "High glycemic load" text to the red region
    fig.add_annotation(
        x= 0.75 * np.max([90, np.max(plot_df["carbs_per_serving"]) + 10]),
        y=110,
        text="High glycemic load (>25)",
        showarrow=False,
        font=dict(color="red", size=14),
        opacity=0.9
    )

    # Add text labels for food names
    fig.add_trace(
        go.Scatter(
            x=plot_df["carbs_per_serving"],
            y=plot_df["gi"],
            mode="text",
            text=plot_df["name"],
            textposition="top right",
            showlegend=False,
            textfont=dict(
                family="Arial",
                size=10,
                color="black"
            )
        )
    )

    # Add hover template to improve hover information display
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br><br>" +
                      "Category: %{customdata[3]}<br>" +
                      "Glycemic Index: %{y:.1f}<br>" +
                      f"Carbs ({serving_size}g): %{{x:.1f}}g<br>" +
                      "Glycemic Load: %{marker.color:.1f}<extra></extra>",
        selector=dict(mode='markers')
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # Show the data table without index
    st.subheader("Food Data Table")
    st.dataframe(df, hide_index=True)

else:
    st.warning("No foods selected. Please choose at least one food category.")

# Add information about the app
st.sidebar.markdown("---")
st.sidebar.info(
    "This app visualizes the glycemic index and glycemic load of various foods. "
    "Adjust the serving size and select food categories to customize the visualization."
)