importPackage(java.io);

TIMEOUT(70000000)
TOPOLOGY = 0;
TX_SUCCESS = "100"
NUM_SAMPLES = 10;
SENSOR_NODE = 4;
ACTUATOR_NODE = 5;
TRES_NODE = 1;
LOGIC_TYPE = "RC";
NUM_NODES = 5;
SENSOR_PERIOD_MS = 6000

function new_file(str) {
    return new FileWriter(LOGIC_TYPE.toLowerCase() + "-tx" + TX_SUCCESS  + "-t" 
    + TOPOLOGY + "-l" + TRES_NODE + str + ".tsv");
}

function init() {
    num_samples = 0;
    delay = -2
    sensor_time = -1; 
    pf_start_time = -1;
    pf_end_time = -1;
    val = -1;
    pf_exec_time = -1
    sens_delay = -1
    act_delay = -1
    file = new_file("");
    t = "\t";
    mylog("Seed: " + sim.getRandomSeed() + "\n");
    mylog("Topology: " + TOPOLOGY + "      TX: " + TX_SUCCESS + "%\n");
    mylog(LOGIC_TYPE + " with logic in node " + TRES_NODE + "\n");
    /* Sensor value, the total delay (from new sensor value to new set point), the 
    * PF computation time, the notification delay (from new sensor value to PF
    * invocation), the actuation delay (from PF termination to new set point) */
    mylog("#\tVal\tDelay\tPF time\tNotif delay\tAct delay\tTraffic\n");
    mylog("\t\t[us]\t[us]\t[us]\t[us]\t[byte]\n");
    powerlog_init();
}

/*-------------------------------------------------------------------------------*/
var powerlog_files = new Array();

function powerlog_init()
{
    for (var i = 1; i <= NUM_NODES; i++) {
        powerlog_files[i] = new_file("-P" + i);
    }
}

function powerlog_stop()
{
    for (var i = 1; i <= NUM_NODES; i++) {
        powerlog_files[i].close();
    }
}

function powerlog() 
{
    if (msg.indexOf("P: ") != -1) {
        powerlog_files[id].write(msg.substring(3) + "\n");
    }
}

function powerlog_wait() 
{
    var done;
    var nodes;
    
    nodes = new Array();
    done = false;
    while (done != true) {
        YIELD_THEN_WAIT_UNTIL(msg.indexOf("P:") != -1);
        nodes[id] = time;
        done = true;
        for (var i = 1; i <= NUM_NODES; i++) {
            if (!nodes[i] || ((time - nodes[i]) > SENSOR_PERIOD_MS * 1000/2.0)) {
                done = false;
            } 
        }
    }
    log.log("sync!\n")
    YIELD_THEN_WAIT_UNTIL(msg.indexOf("P:") != -1);
    
}


/*-------------------------------------------------------------------------------*/
function switch_tres()
{
  data = 0;
  file.close();
  powerlog_stop();
  // stop current tres
  sim.getMoteWithID(TRES_NODE).getInterfaces().getButton().clickButton();
  GENERATE_MSG(60000, "sleep");
  YIELD_THEN_WAIT_UNTIL(msg.equals("sleep"));
  if (TRES_NODE == 5)
    log.testOK();
  // set new tres
  TRES_NODE++;
  init();
  sim.getMoteWithID(TRES_NODE).getInterfaces().getButton().clickButton()
  GENERATE_MSG(120000, "sleep"); //Wait for two min
  YIELD_THEN_WAIT_UNTIL(msg.equals("sleep"));
  powerlog_wait();
}

function mylog(str) {
    log.log(str);
    file.write(str);
}

init();
GENERATE_MSG(5000, "sleep"); //Wait for 5 sec
YIELD_THEN_WAIT_UNTIL(msg.equals("sleep"));
sim.getMoteWithID(TRES_NODE).getInterfaces().getButton().clickButton()
GENERATE_MSG(100000, "sleep"); //Wait for two min
YIELD_THEN_WAIT_UNTIL(msg.equals("sleep"));
powerlog_wait();



plugin = mote.getSimulation().getGUI().
                          getStartedPlugin("se.sics.cooja.plugins.RadioLogger");
while (true) {
    powerlog();
  if (id == SENSOR_NODE && msg.indexOf("S: ") != -1) {
    if (delay == -1) {
        pf_exec_time = pf_end_time - pf_start_time;
        sens_delay = pf_start_time - sensor_time;
        data_size = plugin.getDataTraffic(sensor_time, time);
        mylog((num_samples +1) + t + val + t +t + pf_exec_time +t + sens_delay +t 
            +t + data_size + "\n");
        num_samples++;
    } else if (delay != -2) {
      data_size = plugin.getDataTraffic(sensor_time, time);
      mylog(data_size + "\n");
      num_samples++;
    }
    sensor_time = time;
    pf_start_time = -1
    pf_end_time = -1
    val = msg.substring(3);
    delay = -1;
  }
  if (id == TRES_NODE && msg.equals("F?") && pf_start_time == -1) {
    pf_start_time = time;
  }
  if (id == TRES_NODE && msg.equals("F!") && pf_end_time == -1 ) {
    pf_end_time = time;
  }
  if (id == ACTUATOR_NODE && msg.indexOf("A: ") != -1 && delay == -1) {
    delay = time - sensor_time;
    pf_exec_time = pf_end_time - pf_start_time;
    sens_delay = pf_start_time - sensor_time;
    act_delay = time - pf_end_time;
    mylog((num_samples + 1) + t + val + t + delay + t + pf_exec_time + t 
            + sens_delay + t + act_delay + t);
  }
  YIELD();
  if (num_samples >= NUM_SAMPLES) {
    switch_tres();
    //log.testOK();      
  }

}
