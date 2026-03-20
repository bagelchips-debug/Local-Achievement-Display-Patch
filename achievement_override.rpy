init python in mod_achievement_override:
    
    _constant = True

    from store.achievement import clear_all, Backend, backends
    from store import persistent 
    
    changelog="""
v1.4
  - Chapter 5 Achievements
  - Fixes for upper/lowercase and unknown achievements
v1.3
  - Split into separate files
v1.2
  - Added persistent storage
  - Improvements to achievement name map
v1.1:
  - Now supports the clear() and clear_all() operations
"""
    
    
    if hasattr(renpy.store, "modmanager"):
        renpy.store.modmanager.register_mod(        
            name= "Local Achievements",
            internal="mod_achievement_override",
            version= "1.4.0",
            author= "LordRedStoneNr1",
            settings= "mod_achievement_override_settings",
            changelog=changelog,
        )
    
    
    # this will clear ALL achievements for this game, including Steam!
    def clear_achievements():
        clear_all()
        renpy.notify("Cleared achievements.")
        
    # outside of class, a global method for this mod. 
    # full name: mod_achievement_override.ach_unlocked(key)
    def ach_unlocked(key: str) -> bool:
        return key in persistent._achievements
    
    def ach_image(key: str) -> str:
        if ach_unlocked(key):
            return f"mods/achievement_overrides/achievement_icons/{key}.png"
        else:
            return f"mods/achievement_overrides/achievement_icons/{key}_gray.png"
    
    def ach_name(key: str) -> str:
        return renpy.store.achievement_data.get(key).get("name", key)
    
    def ach_description(key:str) -> str:
        if ach_unlocked(key):
            return renpy.store.achievement_data.get(key).get("description", "")
        else:
            return "???"
        
    def get_ach_progress() -> str:
        unlocked = len(persistent._achievements)
        total = len(renpy.store.achievement_data)
        return f"{unlocked} / {total} Unlocked"  
    
    def get_achievements_by_chapter() -> dict:
        data = renpy.store.achievement_data
        groups = {}
        
        for key, entry in data.items():
            chapter = entry.get("chapter", 0)
            
            if chapter not in groups:
                groups[chapter] = []
            
            # Filter locked achievements
            if persistent.mod_achievement_hide_locked and not ach_unlocked(key):
                continue
            
            groups[chapter].append(key)
        
        # Sort keys in chapter
        # This could be changed to display achievements in logical order (ie end of chapter ach. at the end)
        # But this would probably require even more hard coding
        for chapter in groups:
            groups[chapter].sort(key=lambda k: ach_name(k).lower())
        
        return dict(sorted(groups.items())) # Should return a dictionary of chapters with lists of achievements
    
    if persistent.mod_achievement_override_notifications is None:
        persistent.mod_achievement_override_notifications = True
    
    if persistent.mod_achievement_override_show is None:
        persistent.mod_achievement_override_show = (len(persistent._achievements) > 5)
    
    if persistent.mod_achievement_hide_locked is None:
        persistent.mod_achievement_hide_locked = True
    
    
    class LocalNotificationBackend(Backend):
        ## same as PersistentBackend in 00achievement
        def __init__(self):
            self.stat_max = { }
            self.registered = 0
            self.unlocked = len(persistent._achievements)
        
        def register(self, name, stat_max=None, **kwargs):
            self.registered += 1
            if stat_max:
                self.stat_max[name] = stat_max
    
    
        ## needs to be defined so sync() works and doesn't display things again
        def has(self, name):
             return name in persistent._achievements
             
        ## These two are actually needed to display stuff
        def grant(self, key):
            self.unlocked += 1
            if persistent.mod_achievement_override_notifications:
                renpy.notify("Achievement unlocked: " + ach_name(key))
            
        def progress(self, name, completed):
            if persistent.mod_achievement_override_notifications:
                renpy.notify(get_name(name) + f": ({completed}/{self.stat_max[name]})")
         
        ## so self.unlocked has the right values
        def clear(self, name):
            self.unlocked = len(persistent._achievements)
            
            #Potential bug with clear()
            #If unlock count is updated before the local backend is called, the count will be wrong. 
            # Unlikely to happen because of iteration order but don't rely on it!
            
        def clear_all(self):
            self.unlocked = 0
    
    
    # TODO    
    # Display registered / named achievements (from map) in screen? nah.
    #Improve with images and new screen? Reimplements notify (as a function to show a screen) and stuff?

    lnBackend = LocalNotificationBackend()
    backends.append(lnBackend)
    
screen mod_achievement_override_settings():
    #style_prefix "mod_achievement_override"

    default clear_disclaimer = """This will reset ALL ACHIEVEMENTS for this game,
    including locally and on Steam.
    Continue?"""

    vbox:
        textbutton "Enable Achievement notifications in Ren'Py: [persistent.mod_achievement_override_notifications]" selected False action ToggleVariable("persistent.mod_achievement_override_notifications")
        textbutton "Clear ALL Achievements" action Confirm(clear_disclaimer, Function(mod_achievement_override.clear_achievements))
        hbox:
            text mod_achievement_override.get_ach_progress()
            showif mod_achievement_override.lnBackend.registered > 0:
                text "/[mod_achievement_override.lnBackend.registered]"
                #text "([100.0 * mod_achievement_override.lnBackend.unlocked / mod_achievement_override.lnBackend.registered:.2]%)"
            ## TODO if supported: merge into one textbutton
            showif persistent.mod_achievement_override_show:
                textbutton "Hide Achievement list" selected False action ToggleVariable("persistent.mod_achievement_override_show")
            else:
                textbutton "Show Achievement list" action ToggleVariable("persistent.mod_achievement_override_show")
            showif persistent.mod_achievement_hide_locked:
                textbutton "Show Locked Achievements" selected False action ToggleVariable("persistent.mod_achievement_hide_locked")
            else:
                textbutton "Hide Locked Achievements" action ToggleVariable("persistent.mod_achievement_hide_locked")
        
        spacing 32
        showif persistent.mod_achievement_override_show:
            vbox:
                spacing 16
        
                for chapter, keys in mod_achievement_override.get_achievements_by_chapter().items():
        
                    # Create chapter header
                    text "Chapter [chapter]":
                        size 32
                        bold True
                    
                    vbox:
                        spacing 8
                        
                        for key in keys:
                            
                            $ unlocked = mod_achievement_override.ach_unlocked(key)
                    
                            frame:
                                xminimum 800
                                yminimum 80
                                padding (8, 8)
                                background "#222"
                                
                                hbox:
                                    spacing 6
                    
                                    # Achievement icon
                                    add mod_achievement_override.ach_image(key) xsize 64 ysize 64
                    
                                    vbox:
                                        spacing 2
                    
                                        # Achievement name
                                        text mod_achievement_override.ach_name(key):
                                            yalign 0.0
                                            size 22
                                            if not unlocked:
                                                color "#888"
                    
                                        # Achievement description
                                        if unlocked:
                                            text mod_achievement_override.ach_description(key):
                                                yalign 0.0
                                                size 16
                                                color "#ccc"
                                        else:
                                            text "???":
                                                yalign 0.0
                                                size 16
                                                color "#666"