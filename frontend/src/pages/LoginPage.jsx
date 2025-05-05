// src/pages/LoginPage.jsx


import React from 'react';
import styles from './LoginPage.module.css';

export default function LoginPage() {
  return (
    <div className={styles.loginContainer}>
      <h2 className={styles.loginTitle}>로그인</h2>
      <KakaoLoginButton />
    </div>
  );
}

function KakaoLoginButton() {
  const KAKAO_CLIENT_ID = import.meta.env.VITE_KAKAO_CLIENT_ID;
  const REDIRECT_URI = encodeURIComponent('http://areono.store:3000/redirect'); // const REDIRECT_URI = encodeURIComponent('http://areono.store:
  const STATE = encodeURIComponent('/home');

  const handleLogin = () => {
    const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?response_type=code&client_id=${KAKAO_CLIENT_ID}&redirect_uri=${REDIRECT_URI}&state=${STATE}`;
    window.location.href = kakaoAuthUrl;
  };

  return (
    
    <button className={styles.kakaoLoginButton} onClick={handleLogin}>
      카카오로 시작하기
    </button>
  );
}

//기존 코드
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