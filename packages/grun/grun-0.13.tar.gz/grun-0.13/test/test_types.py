from grun import grun

@grun
def win(
        ImAstring,
        int,                         # type = name
        int_number,
        file,                       # type = name
        file_fichier,
        folder,                 # type = name
        folder_dir,
        bool,               # type = name
        bool_ImBool,
        text,                   # type = name
        text_multilines,
        passwd,                     # type = name
        mot_de_passe_passwd,

        I_m_Boolean_By_Def = True,
        I_m_Integer_By_Def = 12,
        I_m_a_combo_by_def = [1,2,3,"toto"],
        I_m_a_checklist_by_def = (1,2,3,"toto"),


    ):
    return I_m_a_combo_by_def

print win( text=100*"="+"\n*"*20, I_m_a_combo_by_def=2)
