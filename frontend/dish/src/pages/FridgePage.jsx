import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import styles from "./FridgePage.module.css";

export default function FridgePage() {
  const location = useLocation();
  const navigate = useNavigate(); // 하단 요리시작 버튼
  const [ingredients, setIngredients] = useState(
    location.state?.selectedIngredients || []
  );

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedIngredient, setSelectedIngredient] = useState(null);
  const [storedDate, setStoredDate] = useState("");
  const [expireDate, setExpireDate] = useState("");
  const [isFrozen, setIsFrozen] = useState(false);

  // 선택 모드 로직
  const [isSelecting, setIsSelecting] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);

  const handleStoredDateChange = (e) => {
    setStoredDate(e.target.value);
  };

  const handleExpireDateChange = (e) => {
    setExpireDate(e.target.value);
  };

  const handleFreezeToggle = () => {
    setIsFrozen((prev) => !prev);
  };

  // 재료 클릭: 선택모드면 선택 토글, 아니면 모달열기
  const handleIngredientClick = (ingredient) => {
    if (isSelecting) {
      const already = selectedItems.some((i) => i.name === ingredient.name);
      setSelectedItems((prev) =>
        already
          ? prev.filter((i) => i.name !== ingredient.name)
          : [...prev, ingredient]
      );
    } else {
      setSelectedIngredient(ingredient);
      setIsModalOpen(true);
    }
  };

  // 모달 닫기
  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedIngredient(null);
    setStoredDate("");
    setExpireDate("");
    setIsFrozen(false);
  };

  // 소비기한 저장
  const handleSaveDate = () => {
    if (selectedIngredient && expireDate) {
      setIngredients((prev) =>
        prev.map((item) =>
          item.name === selectedIngredient.name ? { ...item, expireDate } : item
        )
      );
      closeModal();
    }
  };

  // 삭제 버튼: 모달에서 선택된 재료를 리스트에서 제거
  const handleDeleteItem = () => {
    if (selectedIngredient) {
      setIngredients((prev) =>
        prev.filter((item) => item.name !== selectedIngredient.name)
      );
      closeModal();
    }
  };

  // 선택모드 토글
  const toggleSelecting = () => {
    setIsSelecting((prev) => {
      if (prev) setSelectedItems([]); // 선택 모드 해제하면 초기화화
      return !prev;
    });
  };

  return (
    <div className={styles.pageContainer}>
      {/* ↗️ 선택모드 버튼 */}
      <button className={styles.selectButton} onClick={toggleSelecting}>
        선택
      </button>

      {/* ↗️ 선택 모드일때만 개수표시 */}
      {isSelecting && (
        <div className={styles.selectedCount}>
          {selectedItems.length}개 선택됨
        </div>
      )}

      <h2 className={styles.pageTitle}>곰이네 냉장고ʕ•ᴥ•ʔ</h2>

      <div className={styles.ingredientsList}>
        {ingredients.map((ingredient) => {
          const isSel = selectedItems.some((i) => i.name === ingredient.name);
          return (
            <div
              key={ingredient.name}
              className={`
                ${styles.ingredientItem}
                ${isSelecting && isSel ? styles.selectedItem : ""}
              `}
              onClick={() => handleIngredientClick(ingredient)}
            >
              <img
                src={ingredient.icon}
                alt={ingredient.name}
                className={styles.ingredientIcon}
              />
              <p className={styles.ingredientName}>
                {ingredient.name}
                {ingredient.expireDate && (
                  <span className={styles.expireDate}>
                    ({ingredient.expireDate})
                  </span>
                )}
              </p>
            </div>
          );
        })}
      </div>

      {/* 모달창 */}
      {isModalOpen && selectedIngredient && (
        <div className={styles.modalBackdrop}>
          <div className={styles.modalContent}>
            <img
              src={selectedIngredient.icon}
              alt={selectedIngredient.name}
              className={styles.modalImage}
            />
            <h2 className={styles.modalTitle}>{selectedIngredient.name}</h2>
            <p className={styles.modalSubtitle}>
              채소{" "}
              {isFrozen && <span style={{ color: "skyblue" }}>냉동 보관</span>}
            </p>

            <div className={styles.dateSection}>
              <div className={styles.dateItem}>
                <span>추가된 날짜</span>
                <input
                  type="date"
                  value={storedDate}
                  onChange={handleStoredDateChange}
                />
              </div>
              <div className={styles.dateItem}>
                <span>소비기한 마감</span>
                <input
                  type="date"
                  value={expireDate}
                  onChange={handleExpireDateChange}
                />
              </div>
            </div>

            <div className={styles.buttonSection}>
              <button
                className={styles.freezeButton}
                onClick={handleFreezeToggle}
              >
                ❄️ 냉동
              </button>
              <button
                className={styles.deleteButton}
                onClick={handleDeleteItem}
              >
                🗑️ 삭제
              </button>
            </div>

            <div className={styles.modalButtons}>
              <button onClick={handleSaveDate}>저장</button>
              <button onClick={closeModal}>닫기</button>
            </div>
          </div>
        </div>
      )}

      {/* 콘텐츠 영역중앙 하단에 고정된 요리시작 버튼 */}
      <button
        className={styles.startButton}
        onClick={() => navigate("/recipe")}
      >
        요리시작
      </button>
    </div>
  );
}
