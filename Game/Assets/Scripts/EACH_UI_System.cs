using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;

namespace EACH.UI {
    public class EACH_UI_System : MonoBehaviour {

        #region Variables 
        [Header("Main Properties")]
        public EACH_UI_Screen m_StartScreen;

        [Header("System Events")]
        public UnityEvent onSwitchedScreen = new UnityEvent();

        [Header("Fader Properties")]
        public Image m_Fader;
        public float m_FadeInDuration = 1f;
        public float m_FadeOutDuration = 1f;

        private Component[] screens = new Component[0];

        private EACH_UI_Screen previousScreen;
        public EACH_UI_Screen PreviousScreen { get { return previousScreen; } }

        private EACH_UI_Screen currentScreen;
        public EACH_UI_Screen CurrentScreen { get { return currentScreen; } }
        #endregion


        #region Main Methods
        // Use this for initialization
        void Start() {
            screens = GetComponentsInChildren<EACH_UI_Screen>(true);
            InitializeScreens();

            if (m_StartScreen) {
                SwitchScreens(m_StartScreen);
            }
            if (m_Fader) {
                m_Fader.gameObject.SetActive(true);
            }
            FadeIn();
        }
        #endregion

        #region Helper Methods
        public void SwitchScreens(EACH_UI_Screen aScreen) {
            if (aScreen) {
                if (currentScreen) {
                    currentScreen.CloseScreen();
                    previousScreen = currentScreen;
                }
                currentScreen = aScreen;
                currentScreen.gameObject.SetActive(true);
                currentScreen.StartScreen();
                Debug.Log("DAAMNTRIG");

                if (onSwitchedScreen != null) {
                    onSwitchedScreen.Invoke();
                }
            }

        }

        public void FadeIn() {
            if (m_Fader) {
                Debug.Log("FADE_LAUNCH");
                m_Fader.CrossFadeAlpha(0f, m_FadeInDuration, false);
            }
        }
        public void FadeOut() {
            if (m_Fader) {
                m_Fader.CrossFadeAlpha(1f, m_FadeOutDuration, false);
            }
        }
        public void GoToPreviousScreen() {
            if (previousScreen) {
                SwitchScreens(previousScreen);
            }
        }
        public void LoadScene(int sceneIndex) {
            StartCoroutine(WaitToLoadScene(sceneIndex));
        }
        IEnumerator WaitToLoadScene(int sceneIndex) {
            yield return null;
        }
        void InitializeScreens() {
            foreach (var screen in screens) {
                screen.gameObject.SetActive(true);
            }
        }
        #endregion
    }
}
