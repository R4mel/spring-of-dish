import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import styles from './FridgePage.module.css'; 


export default function FridgePage() {
  const location = useLocation();
  const [ingredients, setIngredients] = useState(location.state?.selectedIngredients || []);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedIngredient, setSelectedIngredient] = useState(null);
  const [selectedDate, setSelectedDate] = useState('')

  const [isFrozen, setIsFrozen] = useState(false);
  const [storedDate, setStoredDate] = useState('');
  const [expireDate, setExpireDate] = useState('');

  const handleStoredDateChange = (e) => {
    setStoredDate(e.target.value);
  };
  
  const handleExpireDateChange = (e) => {
    setExpireDate(e.target.value);
  };

  const handleFreezeToggle = () => {
    setIsFrozen((prev) => !prev);
  };
  
  
  // 👉 재료 클릭하면 모달 열기
  const handleIngredientClick = (ingredient) => {
    setSelectedIngredient(ingredient);
    setIsModalOpen(true);
  };

  // 👉 모달 닫기
  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedIngredient(null);
  };


  // 날짜 input이 바뀔때
  const handleDateChange = (e) => {
    setSelectedDate(e.target.value);
  };

  
  const handleDeleteItem = () => {
    // 삭제 로직 (선택한 재료 삭제)
    console.log('삭제됨!');
    closeModal();
  };
  
  // 저장 버튼 눌렀을 때 
  const handleSaveDate = () => {
    if (selectedIngredient && selectedDate) {
      const updatedIngredients = ingredients.map(item => {
        if (item.name === selectedIngredient.name) {
          return { ...item, expireDate: selectedDate };
        }
        return item;
      });
      setIngredients(updatedIngredients); // 재료 리스트 업데이트
      closeModal(); // 모달 닫기
    }
  };

  return (
    <div className={styles.pageContainer}>
      <h2 className={styles.pageTitle}>곰이네 냉장고ʕ•ᴥ•ʔ</h2>

      <div className={styles.ingredientsList}>
        {ingredients.map((ingredient) => (
          <div
            key={ingredient.name}
            className={styles.ingredientItem}
            onClick={() => handleIngredientClick(ingredient)}
          >
            <img src={ingredient.icon} alt={ingredient.name} className={styles.ingredientIcon} />
            <p className={styles.ingredientName}>
              {ingredient.name}
              {/* ✨ 소비기한 있으면 같이 보여주기 */}
              {ingredient.expireDate && (
                <div className={styles.expireDate}>
                  ({ingredient.expireDate})
                </div>
              )}
            </p>
          </div>
        ))}
      </div>

      {/* 모달 */}
      {isModalOpen && selectedIngredient && (
      <div className={styles.modalBackdrop}>
        <div className={styles.modalContent}>

          {/* 상단: 재료 아이콘 + 이름 */}
          <img src={selectedIngredient.icon} alt={selectedIngredient.name} className={styles.modalImage} />
          <h2 className={styles.modalTitle}>{selectedIngredient.name}</h2>
          <p className={styles.modalSubtitle}>
            채소 {isFrozen && <span style={{ color: 'skyblue' }}>냉동 보관</span>}
          </p>

          {/* 날짜 입력 */}
          <div className={styles.dateSection}>
            <div className={styles.dateItem}>
              <span>추가된 날짜</span>
              <input type="date" value={storedDate} onChange={handleStoredDateChange} />
            </div>
            <div className={styles.dateItem}>
              <span>소비기한 마감</span>
              <input type="date" value={expireDate} onChange={handleExpireDateChange} />
            </div>
          </div>

          {/* 냉동/삭제 버튼 */}
          <div className={styles.buttonSection}>
            <button className={styles.freezeButton} onClick={handleFreezeToggle}>❄️ 냉동</button>
            <button className={styles.deleteButton} onClick={handleDeleteItem}>🗑️ 삭제</button>
          </div>

          {/* 저장/닫기 버튼 */}
          <div className={styles.modalButtons}>
            <button onClick={handleSaveDate}>저장</button>
            <button onClick={closeModal}>닫기</button>
          </div>

        </div>
      </div>
      )}
    </div>
  );
}