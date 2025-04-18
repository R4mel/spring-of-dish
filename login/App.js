import React, { useState } from "react";

function HomePage() {
  const [selectedIngredients, setSelectedIngredients] = useState([]);

  const toggleIngredient = (ingredient) => {
    if (selectedIngredients.includes(ingredient)) {
      const newList = selectedIngredients.filter((item) => item !== ingredient);
      setSelectedIngredients(newList);
    } else {
      const newList = [...selectedIngredients, ingredient];
      setSelectedIngredients(newList);
    }
  };

  return (
    <div
      style={{
        width: "390px",
        height: "844px",
        margin: "0 auto",
        fontFamily: "sans-serif",
        display: "flex",
        flexDirection: "column",
        border: "1px solid lightgray",
      }}
    >
      {/* 상단 네비게이션 바 */}
      <div
        style={{
          backgroundColor: "#64C826",
          padding: "16px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div></div>
        <div
          style={{
            color: "white",
            fontSize: "18px",
            fontWeight: "bold",
          }}
        >
          홈
        </div>
        <button
          style={{
            backgroundColor: "transparent",
            border: "none",
            color: "white",
            fontSize: "24px",
            cursor: "pointer",
          }}
        >
          +
        </button>
      </div>

      {/* 메인 콘텐츠 */}
      <div
        style={{
          padding: "24px",
          flex: 1,
          display: "flex",
          flexDirection: "column",
          position: "relative",
        }}
      >
        {selectedIngredients.length > 0 && (
          <div
            style={{
              position: "absolute",
              top: "16px",
              right: "24px",
              color: "#64C826",
              fontSize: "14px",
            }}
          >
            {selectedIngredients.length}개 선택됨
          </div>
        )}

        <h2 style={{ color: "#64C826", marginBottom: "16px" }}>식재료</h2>

        <div
          style={{
            display: "flex",
            gap: "12px",
            flexWrap: "wrap",
            marginBottom: "32px",
          }}
        >
          {["계란", "쌀", "대파"].map((item) => {
            const isSelected = selectedIngredients.includes(item);
            return (
              <button
                key={item}
                onClick={() => toggleIngredient(item)}
                style={{
                  padding: "8px 16px",
                  borderRadius: "4px",
                  border: "1px solid #ccc",
                  backgroundColor: isSelected ? "#64C826" : "#f0f0f0",
                  color: isSelected ? "#fff" : "#000",
                  cursor: "pointer",
                }}
              >
                {item}
              </button>
            );
          })}
        </div>

        <button
          style={{
            backgroundColor: "#64C826",
            color: "white",
            border: "none",
            borderRadius: "30px",
            width: "180px",
            height: "48px",
            fontSize: "16px",
            cursor: "pointer",
            alignSelf: "center",
            marginTop: "auto",
            marginBottom: "24px",
          }}
        >
          요리시작!
        </button>
      </div>

      {/* 하단 네비게이션 바 */}
      <div
        style={{
          backgroundColor: "#64C826",
          padding: "12px 0",
          display: "flex",
          justifyContent: "space-around",
        }}
      >
        <button
          style={{
            backgroundColor: "transparent",
            border: "none",
            color: "white",
            fontSize: "16px",
            cursor: "pointer",
          }}
        >
          홈
        </button>
        <button
          style={{
            backgroundColor: "transparent",
            border: "none",
            color: "white",
            fontSize: "16px",
            cursor: "pointer",
          }}
        >
          즐겨찾기
        </button>
      </div>
    </div>
  );
}

export default HomePage;
