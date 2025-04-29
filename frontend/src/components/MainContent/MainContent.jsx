// import React from 'react';
// import styles from './MainContent.module.css';

// function MainContent() {
//   return (
//     <main className={styles.main}>
//       <div className={styles.imageWrapper}>
//         {/* 이미지 예시 */}
//         <img
//           src="/home/compute01/docker/frontend/public/fre.png"
//           alt="예시 이미지"
//           className={styles.mainImage}
//         />
//       </div>
//       <h2 className={styles.title}>냉장고가 비었어요!</h2>
//       <p className={styles.description}>
//         냉장고의 재료를 등록하고 <br />
//         바로 만들 수 있는 레시피를 확인해보세요.
//       </p>
//     </main>
//   );
// }

// export default MainContent;
import React from 'react';
import styles from './MainContent.module.css';

function MainContent() {
  const handleImageError = (e) => {
    e.target.src = '/home/compute01/docker/frontend/public/fre.png'; // 로컬 기본 이미지로 대체
  };

  return (
    <main className={styles.main}>
      <div className={styles.imageWrapper}>
        <img
          src="/home/compute01/docker/frontend/public/fre.png" // 안정적인 placeholder 사용
          alt="예시 이미지"
          className={styles.mainImage}
          onError={handleImageError} // 로딩 실패 시 대체
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