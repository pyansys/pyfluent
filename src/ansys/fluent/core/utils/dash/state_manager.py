
from post_windows import PlotWindowCollection, GraphicsWindowCollection
from app_defn import app
class StateManager:
    _states = {}

    def __init__(self, user_id, session_id, SessionsManager):
        unique_id = f"{user_id}-{session_id}"
        state = StateManager._states.get(unique_id)
        if not state:
            self._user_id = user_id
            self._session_id = session_id
            self._sessions_manager = SessionsManager
            self._session_handle = SessionsManager(app, user_id, session_id)
        else:
            self.__dict__ = state
            
    def copy_from(self, user_id, session_id):
        PlotWindowCollection(
            app, self._user_id, self._session_id, self._sessions_manager
        ).copy_from(user_id, session_id)
        
        GraphicsWindowCollection(
            app, self._user_id, self._session_id, self._sessions_manager
        ).copy_from(user_id, session_id)

        self._sessions_manager._sessions_state[
            self._session_handle._complete_session_id
        ] = self._sessions_manager._sessions_state[
            self._sessions_manager(app, user_id, session_id)._complete_session_id
        ]    

  