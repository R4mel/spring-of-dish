import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './MainContent.module.css';

function MainContent() {
  const navigate = useNavigate();
  return (
    <main className={styles.main}>
      <div className={styles.imageWrapper}>
        {/* 이미지 예시 */}
        <img
          src="assets/refrigerator.png"
          alt="냉장고 이미지"
          className={styles.mainImage}
        />
      </div>
      <h2 className={styles.title}>냉장고가 비었어요!</h2>
      <p className={styles.description}>
        냉장고에 재료를 추가하고 <br />
        레시피를 추천 받아보세요!
      </p>

      {/* 요리시작 버튼 */}
      <button
        className={styles.startButton}
        onClick={() => navigate('/recipe')}
      >
        요리시작
      </button>
    </main>
  );
}

export default MainContent;
