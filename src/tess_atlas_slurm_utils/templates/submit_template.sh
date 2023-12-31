#!/bin/bash

GENERATION_FN=({{generation_fns}})
ANALYSIS_FN=({{analysis_fns}})
ANLYS_IDS=()

{% if partition!="" -%}
PARTITION="--partition={{partition}}"
{% else %}
PARTITION=""
{% endif %}

for index in ${!ANALYSIS_FN[*]}; do
  if [ ! -z $GENERATION_FN ]; then
    >&2 echo "Submitting ${GENERATION_FN[$index]} ${ANALYSIS_FN[$index]}"
    GEN_ID=$(sbatch --partition=datamover --parsable ${GENERATION_FN[$index]})
    ANLYS_ID=$(sbatch $PARTITION --parsable --dependency=aftercorr:$GEN_ID ${ANALYSIS_FN[$index]})
  else
    >&2 echo "Submitting ${GENERATION_FN[$index]}}"
    ANLYS_ID=$(sbatch $PARTITION --parsable ${ANALYSIS_FN[$index]})
  fi
  ANLYS_IDS+=($ANLYS_ID)
done

for item in "${ANLYS_IDS[@]}"; do
  echo "$item"
done

>&2 squeue -u $USER -o '%.4u %.20j %.10A %.4C %.10E %R'
