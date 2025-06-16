import altair as alt
import pandas as pd
import streamlit as st

st.title("领导班子评分折算系统（最终版）")

# 基准分参数设置
st.header("基准参数设置")
col_a, col_b = st.columns(2)
with col_a:
    a_benchmark = st.number_input("班子基准最高分(A)", step=0.1)
with col_b:
    b_benchmark = st.number_input("班子基准最低分(B)", step=0.1)

# 原始分数输入模块
st.header("原始评分输入")
raw_scores = st.text_area("输入原始评分（每行一个）")

try:
    # 数据转换与校验
    scores = [float(x.strip()) for x in raw_scores.split("\n") if x.strip()]
    
    if len(scores) < 3:
        st.error("错误：至少需要3个有效评分")
    else:
        # 核心参数计算
        d_original = max(scores)
        e_original = min(scores)
        f_original = d_original - e_original
        c_value = a_benchmark - b_benchmark

        # 参数展示表格
        param_df = pd.DataFrame({
            "参数名称": ["A(基准最高)", "B(基准最低)", "D(原始最高)", 
                     "E(原始最低)", "C(赋分区间)", "F(原始区间)"],
            "数值": [a_benchmark, b_benchmark, d_original, 
                  e_original, c_value, f_original]
        })
        st.subheader("核心参数概览")
        st.table(param_df.style.format({"数值": "{:.2f}"}))

        # 分数折算逻辑
        results = []
        for g in scores:
            if g == d_original:
                res = a_benchmark
                logic = "最高分→A"
            elif g == e_original:
                res = min(g, b_benchmark)  # 保证不高于B
                logic = f"最低分→{res}"
            else:
                if g <= b_benchmark:
                    res = g
                    logic = "原分≤B保留"
                else:
                    calc_res = a_benchmark - ((d_original - g)/f_original) * c_value
                    res = g if calc_res < b_benchmark else calc_res
                    logic = "计算保留" if calc_res < b_benchmark else "正常折算"
            results.append((round(res, 2), logic))

        # 结果展示
        st.subheader("评分折算明细")
        result_df = pd.DataFrame({
            "原始评分": scores,
            "折算结果": [x[0] for x in results],
            "处理逻辑": [x[1] for x in results]
        })
        
        # 颜色标注规则
        def highlight_cells(row):
            colors = {
                "最高分→A": 'background-color: #C8E6C9',
                "最低分→B": 'background-color: #FFCDD2',
                "原分≤B保留": 'background-color: #B3E5FC',
                "计算保留": 'background-color: #FFF9C4',
                "正常折算": ''
            }
            return [colors.get(row['处理逻辑'], '')]*3

        st.dataframe(
            result_df.style.apply(highlight_cells, axis=1)
                          .format({"原始评分": "{:.2f}", "折算结果": "{:.2f}"}),
            height=800,
            use_container_width=True
        )

except ValueError:
    st.error("输入包含非数字内容，请检查数据格式")
