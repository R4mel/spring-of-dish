// // src/pages/LoginPage.jsx
// import React from 'react';
// import styles from './LoginPage.module.css';

// export default function LoginPage() {
//   // Vite 환경변수로부터 Kakao OAuth 정보 가져오기
//   const kakaoClientId = import.meta.env.VITE_KAKAO_CLIENT_ID;
//   const redirectUri = import.meta.env.VITE_KAKAO_REDIRECT_URI;
//   const kakaoAuthUrl =
//     `https://kauth.kakao.com/oauth/authorize` +
//     `?client_id=${kakaoClientId}` +
//     `&redirect_uri=${encodeURIComponent(redirectUri)}` +
//     `&response_type=code`;

//   return (
//     <div className={styles.loginContainer}>
//       <h2 className={styles.loginTitle}>로그인</h2>
//       <button
//         className={styles.kakaoLoginButton}
//         onClick={() => {
//           window.location.href = kakaoAuthUrl;
//         }}
//       >
//         카카오로 시작하기
//       </button>
//     </div>
//   );
// }

import React from 'react';
import styles from './LoginPage.module.css';

/**
 * LoginPage.jsx
 *
 * - 백엔드의 /authorize 엔드포인트를 호출하여 카카오 인증 페이지로 리다이렉트합니다.
 * - 환경 변수 VITE_API_URL에 설정된 백엔드 URL을 사용합니다.
 */
export default function LoginPage() {
  // 백엔드 API 베이스 URL
  const API_URL = import.meta.env.VITE_API_URL;
  // /authorize 엔드포인트 호출
  const kakaoAuthUrl = `${API_URL}/authorize`;

  return (
    <div className={styles.loginContainer}>
      <h2 className={styles.loginTitle}>로그인</h2>
      <button
        className={styles.kakaoLoginButton}
        onClick={() => {
          window.location.href = kakaoAuthUrl;
        }}
      >
        카카오로 시작하기
      </button>
    </div>
  );
}
