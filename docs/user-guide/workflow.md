
## In-Between Names

To help you keep track of in-betweens, the in-between shape key's name is auto-generated and updated depending on the hero shape key's name and the activation value. For example, if the hero shape key is named *smile.L* an in-between shape key with an activation value of 0.3 will be named *smile_0.300.L*

!!! warning
    Blender imposes a 64 character limit to shape key names. Because in-between names are suffixed with up to 7 characters, the character limit for hero shape keys should be considered to be 57.


!!! note
    Though rarely needed, it is possible to add in-betweens to in-betweens. This allows for cases where an animator working downstream in the pipeline wants to adjust the way an in-between works while leaving the already present in-between intact.