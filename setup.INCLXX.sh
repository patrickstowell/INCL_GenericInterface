#!/bin/sh

#export INCL_SRC=/Users/stowell/Research/Development/NUISANCEMC/generator/inclcxx-fork-fsimode
#export INCL_SRC=/Users/stowell/Research/Development/NUISANCEMC/INCL_DEV/INCLannaRemerged
export INCL_ROOT=/software/incl-generic-interface/
export INCL_SRC=$INCL_ROOT/
export INCL_BIN_DIR=/software/incl-build/

export ABLA_DATA=$INCL_ROOT/de-excitation/abla07/upstream/tables/
export INCL_DATA=$INCL_ROOT/data/

export INCL_SRC_INC_DIRS=$(find $INCL_SRC -type f \( -name "*.hh" -o -name "*.h" \) -exec dirname {} \; | sort -u | sed 's/^/-I/' | tr '\n' ' ')
export INCL_BUILD_INC_DIRS=$(find $INCL_ROOT -type f \( -name "*.hh" -o -name "*.h" \) -exec dirname {} \; | sort -u | sed 's/^/-I/' | tr '\n' ' ')
export INCL_INC_DIRS="$INCL_SRC_INC_DIRS $INCL_BUILD_INC_DIRS"

export INCL_LIB_DIRS=$(find $INCL_ROOT -type f \( -name "*.so" -o -name "*.a" \) -exec dirname {} \; | sort -u | tr '\n' ':' | sed 's/:$//')
export INCL_LIB_LINKING_DIRS=$(find $INCL_ROOT -type f \( -name "*.so" -o -name "*.a" \) -exec dirname {} \; | sort -u | sed 's|^|-L|' | tr '\n' ' ')
export INCL_LIBS=$(find $INCL_ROOT -type f \( -name "*.so" -o -name "*.a" \) -exec basename {} \; | sed -E 's/^lib(.*)\.(so|a)$/-l\1/' | tr '\n' ' ')
export INCL_LINK="$INCL_LIB_LINKING_DIRS $INCL_LIBS"

export INCL_BUILD_FLAGS="HAS_BOOST_DATE_TIME;HAS_BOOST_TIMER;HAS_BOOST_PROGRAM_OPTIONS;INCL_SIGNAL_HANDLING;INCL_ROOT_USE;INCL_DEBUG_LOG;INCL_AVATAR_SEARCH_MinElement;INCL_CACHING_CLUSTERING_MODEL_INTERCOMPARISON_Set;G4ThreadLocal=;INCL_USE_ALLOCATION_POOL;HAVE_WORDEXP;INCL_DEEXCITATION_FERMI_BREAKUP;INCL_DEEXCITATION_ABLA07;INCL_DEEXCITATION_ABLAXX;INCL_DEEXCITATION_GEMINIXX;INCL_DEEXCITATION_SMM;ABLA07_USE_USER_RNG;GEMINIXX_USE_USER_RNG;SMM_USE_USER_RNG"

export LD_LIBRARY_PATH=$INCL_LIB_DIRS:$LD_LIBRARY_PATH
export PATH=$INCL_BIN_DIR:$PATH
