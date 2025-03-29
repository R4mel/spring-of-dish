import React from 'react';
import styles from './MainContent.module.css';

function MainContent() {
  return (
    <main className={styles.main}>
      <div className={styles.imageWrapper}>
        {/* 이미지 예시 */}
        <img
          src="https://via.placeholder.com/150"
          alt="예시 이미지"
          className={styles.mainImage}
        />
      </div>
      <h2 className={styles.title}>냉장고가 비었어요!</h2>
      <p className={styles.description}>
        냉장고의 재료를 등록하고 <br />
        바로 만들 수 있는 레시피를 확인해보세요.
      </p>
    </main>
  );
}

export default MainContent;
