
// import React, { useEffect } from 'react';
// import { useSearchParams, useNavigate } from 'react-router-dom';

// export default function OAuthCallback() {
//   const [searchParams] = useSearchParams();
//   const navigate = useNavigate();

//   useEffect(() => {
//     const code = searchParams.get('code');
//     if (!code) {
//       // 에러 처리
//       alert('인가 코드가 없습니다');
//       navigate('/login');
//       return;
//     }

//     // 백엔드에 code 전송하여 토큰 받기
//     fetch('http://areono.store:8000/auth/kakao/callback?code=' + code)
//       .then(res => res.json())
//       .then(data => {
//         // 예: 로컬 스토리지에 저장
//         localStorage.setItem('access_token', data.access_token);
//         // 메인 페이지 이동
//         navigate('/');
//       })
//       .catch(err => {
//         console.error(err);
//         alert('로그인 중 오류가 발생했습니다');
//         navigate('/login');
//       });
//   }, [searchParams, navigate]);

//   return (
//     <div style={{
//       display:'flex', alignItems:'center', justifyContent:'center',
//       height:'100vh'
//     }}>
//       <p>로그인 처리 중…</p>
//     </div>
//   );
// }

import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

/**
 * OAuthCallbackPage.jsx
 *
 * - URL의 code 파라미터를 읽어 백엔드 /redirect 엔드포인트로 전송
 * - JWT와 사용자 정보를 받아 localStorage에 저장 후 HomePage로 이동
 */
export default function OAuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const code = searchParams.get('code');
    if (!code) {
      alert('인가 코드가 없습니다. 로그인 페이지로 이동합니다.');
      return navigate('/login');
    }

    const API_URL = import.meta.env.VITE_API_URL;
    fetch(`${API_URL}/redirect?code=${encodeURIComponent(code)}`)
      .then(async res => {
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || res.statusText);
        }
        return res.json();
      })
      .then(data => {
        // JWT 저장
        localStorage.setItem('jwt_token', data.jwt_token);
        // 사용자 정보 필요한 경우 state로 전달
        navigate('/', { state: { user: data.user } });
      })
      .catch(err => {
        console.error('OAuthCallback Error:', err);
        alert(`로그인 중 오류가 발생했습니다: ${err.message}`);
        navigate('/login');
      });
  }, [searchParams, navigate]);

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
    }}>
      <p>로그인 처리 중… 잠시만 기다려주세요.</p>
    </div>
  );
}
